from typing import Optional

from fastapi import HTTPException
from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.device_model import Device
from app.models.loan_model import Loan
from app.schemas.device_schema import DeviceCreate, DevicePatch, DeviceUpdate


def list_devices(
    db: Session,
    device_type: Optional[str] = None,
    is_available: Optional[bool] = None,
    brand: Optional[str] = None,
    search: Optional[str] = None,
) -> list[Device]:
    filters = []
    if device_type:
        filters.append(Device.device_type.ilike(device_type))
    if is_available is not None:
        filters.append(Device.is_available == is_available)
    if brand:
        filters.append(Device.brand.ilike(brand))
    if search:
        term = f"%{search.strip()}%"
        filters.append(or_(Device.name.ilike(term), Device.serial_number.ilike(term), Device.brand.ilike(term)))
    query = db.query(Device)
    if filters:
        query = query.filter(and_(*filters))
    return query.order_by(Device.id).all()


def get_device(db: Session, device_id: int) -> Device:
    device = db.query(Device).filter(Device.id == device_id).first()
    if device is None:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    return device


def _ensure_unique_serial(db: Session, serial_number: str, exclude_id: Optional[int] = None) -> None:
    query = db.query(Device).filter(Device.serial_number == serial_number)
    if exclude_id is not None:
        query = query.filter(Device.id != exclude_id)
    if query.first():
        raise HTTPException(status_code=400, detail="El número de serie ya está registrado")


def create_device(db: Session, data: DeviceCreate) -> Device:
    _ensure_unique_serial(db, data.serial_number)
    device = Device(**data.model_dump())
    db.add(device)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="El número de serie ya está registrado")
    db.refresh(device)
    return device


def _ensure_availability_can_change(db: Session, device: Device, available: Optional[bool]) -> None:
    if available is True and db.query(Loan).filter(Loan.device_id == device.id, Loan.status.in_(("active", "overdue"))).first():
        raise HTTPException(status_code=409, detail="No se puede marcar disponible mientras tenga un préstamo activo")


def update_device(db: Session, device: Device, data: DeviceUpdate | DevicePatch, partial: bool = False) -> Device:
    updates = data.model_dump(exclude_unset=partial)
    if "serial_number" in updates:
        _ensure_unique_serial(db, updates["serial_number"], exclude_id=device.id)
    _ensure_availability_can_change(db, device, updates.get("is_available"))
    for field, value in updates.items():
        setattr(device, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="El número de serie ya está registrado")
    db.refresh(device)
    return device


def delete_device(db: Session, device: Device) -> None:
    if db.query(Loan).filter(Loan.device_id == device.id).first():
        raise HTTPException(status_code=409, detail="No se puede eliminar un dispositivo con historial de préstamos")
    db.delete(device)
    db.commit()