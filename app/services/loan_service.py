from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload

from app.models.device_model import Device
from app.models.loan_model import Loan
from app.models.user_model import User
from app.schemas.loan_schema import LoanCreate


def list_loans(
    db: Session,
    loan_status: Optional[str] = None,
    user_email: Optional[str] = None,
    device_type: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
) -> list[Loan]:
    query = db.query(Loan).join(Loan.user).join(Loan.device).options(
        joinedload(Loan.user), joinedload(Loan.device)
    )
    filters = []
    if loan_status:
        filters.append(Loan.status == loan_status)
    if user_email:
        filters.append(User.email.ilike(user_email))
    if device_type:
        filters.append(Device.device_type.ilike(device_type))
    if date_from:
        filters.append(Loan.loan_date >= date_from)
    if date_to:
        filters.append(Loan.loan_date <= date_to)
    if filters:
        query = query.filter(and_(*filters))
    return query.order_by(Loan.loan_date.desc(), Loan.id.desc()).all()


def get_loan(db: Session, loan_id: int) -> Loan:
    loan = (
        db.query(Loan)
        .options(joinedload(Loan.user), joinedload(Loan.device))
        .filter(Loan.id == loan_id)
        .first()
    )
    if loan is None:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")
    return loan


def create_loan(db: Session, data: LoanCreate) -> Loan:
    user = db.query(User).filter(User.id == data.user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    device = db.query(Device).filter(Device.id == data.device_id).with_for_update().first()
    if device is None:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    if not device.is_available:
        raise HTTPException(status_code=409, detail="El dispositivo no está disponible")

    loan = Loan(user_id=user.id, device_id=device.id, status="active")
    device.is_available = False
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan


def return_loan(db: Session, loan_id: int) -> Loan:
    loan = get_loan(db, loan_id)
    if loan.status == "returned":
        raise HTTPException(status_code=409, detail="El préstamo ya fue devuelto")
    loan.status = "returned"
    loan.return_date = datetime.now(timezone.utc).replace(tzinfo=None)
    loan.device.is_available = True
    db.commit()
    db.refresh(loan)
    return loan


def list_user_loans(db: Session, user_id: int) -> list[Loan]:
    user = db.query(User.id).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return (
        db.query(Loan)
        .join(Loan.device)
        .options(joinedload(Loan.user), joinedload(Loan.device))
        .filter(Loan.user_id == user_id)
        .order_by(Loan.loan_date.desc())
        .all()
    )


def list_device_loans(db: Session, device_id: int) -> list[Loan]:
    device = db.query(Device.id).filter(Device.id == device_id).first()
    if device is None:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    return (
        db.query(Loan)
        .join(Loan.user)
        .options(joinedload(Loan.user), joinedload(Loan.device))
        .filter(Loan.device_id == device_id)
        .order_by(Loan.loan_date.desc())
        .all()
    )