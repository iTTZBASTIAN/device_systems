from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db
from app.schemas.device_schema import DeviceCreate, DevicePatch, DeviceResponse, DeviceUpdate
from app.schemas.loan_schema import LoanDetailResponse
from app.services import device_service, loan_service

router = APIRouter(prefix="/devices", tags=["Devices"])


@router.get(
    "",
    response_model=list[DeviceResponse],
    summary="Listar dispositivos",
    description="Lista y filtra dispositivos por tipo, disponibilidad, marca o texto libre.",
    response_description="Dispositivos que coinciden con los filtros.",
)
def list_devices(
    device_type: Optional[str] = Query(None, min_length=1),
    is_available: Optional[bool] = None,
    brand: Optional[str] = Query(None, min_length=1),
    search: Optional[str] = Query(None, min_length=1),
    db: Session = Depends(get_db),
):
    return device_service.list_devices(db, device_type, is_available, brand, search)


@router.post(
    "",
    response_model=DeviceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear dispositivo",
    response_description="Dispositivo creado y disponible para préstamo.",
    responses={400: {"description": "Número de serie duplicado."}},
)
def create_device(data: DeviceCreate, db: Session = Depends(get_db)):
    return device_service.create_device(db, data)


@router.get(
    "/{device_id}/loans",
    response_model=list[LoanDetailResponse],
    summary="Consultar historial de un dispositivo",
    description="Devuelve los préstamos del dispositivo con información de usuario y equipo.",
    response_description="Historial de préstamos del dispositivo.",
    responses={404: {"description": "Dispositivo no encontrado."}},
)
def get_device_loans(device_id: int, db: Session = Depends(get_db)):
    return loan_service.list_device_loans(db, device_id)


@router.get(
    "/{device_id}",
    response_model=DeviceResponse,
    summary="Consultar dispositivo por ID",
    responses={404: {"description": "Dispositivo no encontrado."}},
)
def get_device(device_id: int, db: Session = Depends(get_db)):
    return device_service.get_device(db, device_id)


@router.put(
    "/{device_id}",
    response_model=DeviceResponse,
    summary="Reemplazar dispositivo",
    description="Actualiza todos los datos editables del dispositivo.",
    responses={400: {"description": "Número de serie duplicado."}, 404: {"description": "Dispositivo no encontrado."}, 409: {"description": "Estado incompatible con un préstamo activo."}},
)
def update_device(device_id: int, data: DeviceUpdate, db: Session = Depends(get_db)):
    device = device_service.get_device(db, device_id)
    return device_service.update_device(db, device, data)


@router.patch(
    "/{device_id}",
    response_model=DeviceResponse,
    summary="Actualizar dispositivo parcialmente",
    responses={400: {"description": "Número de serie duplicado."}, 404: {"description": "Dispositivo no encontrado."}, 409: {"description": "Estado incompatible con un préstamo activo."}, 422: {"description": "No se enviaron campos válidos."}},
)
def patch_device(device_id: int, data: DevicePatch, db: Session = Depends(get_db)):
    if not data.model_fields_set:
        raise HTTPException(status_code=422, detail="Debe enviar al menos un campo")
    device = device_service.get_device(db, device_id)
    return device_service.update_device(db, device, data, partial=True)


@router.delete(
    "/{device_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar dispositivo",
    response_description="El dispositivo fue eliminado.",
    responses={404: {"description": "Dispositivo no encontrado."}, 409: {"description": "El dispositivo tiene historial de préstamos."}},
)
def delete_device(device_id: int, db: Session = Depends(get_db)) -> Response:
    device = device_service.get_device(db, device_id)
    device_service.delete_device(db, device)
    return Response(status_code=status.HTTP_204_NO_CONTENT)