from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db
from app.schemas.loan_schema import LoanCreate, LoanDetailResponse, LoanResponse, LoanStatus
from app.services import loan_service

router = APIRouter(prefix="/loans", tags=["Loans"])


def _validate_date_range(date_from: Optional[datetime], date_to: Optional[datetime]) -> None:
    if date_from and date_to and date_from > date_to:
        raise HTTPException(status_code=422, detail="date_from no puede ser posterior a date_to")


@router.get(
    "/details",
    response_model=list[LoanDetailResponse],
    summary="Listar préstamos con información relacionada",
    description="Combina préstamos, usuarios y dispositivos mediante joins; admite filtros combinables.",
    response_description="Préstamos con usuario y dispositivo asociados.",
)
def list_loan_details(
    loan_status: Optional[LoanStatus] = Query(None, alias="status"),
    user_email: Optional[str] = Query(None, min_length=3),
    device_type: Optional[str] = Query(None, min_length=1),
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    _validate_date_range(date_from, date_to)
    return loan_service.list_loans(db, loan_status, user_email, device_type, date_from, date_to)


@router.get(
    "",
    response_model=list[LoanDetailResponse],
    summary="Listar y filtrar préstamos",
    description="Filtra por estado, correo del usuario, tipo de dispositivo y rango de fechas.",
    response_description="Préstamos con la información de usuario y dispositivo.",
)
def list_loans(
    loan_status: Optional[LoanStatus] = Query(None, alias="status"),
    user_email: Optional[str] = Query(None, min_length=3),
    device_type: Optional[str] = Query(None, min_length=1),
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    _validate_date_range(date_from, date_to)
    return loan_service.list_loans(db, loan_status, user_email, device_type, date_from, date_to)


@router.post(
    "",
    response_model=LoanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Prestar un dispositivo",
    description="Valida usuario y disponibilidad; crea el préstamo y marca el dispositivo como no disponible.",
    responses={404: {"description": "Usuario o dispositivo no encontrado."}, 409: {"description": "El dispositivo no está disponible."}},
)
def create_loan(data: LoanCreate, db: Session = Depends(get_db)):
    return loan_service.create_loan(db, data)


@router.get(
    "/{loan_id}",
    response_model=LoanDetailResponse,
    summary="Consultar préstamo por ID",
    responses={404: {"description": "Préstamo no encontrado."}},
)
def get_loan(loan_id: int, db: Session = Depends(get_db)):
    return loan_service.get_loan(db, loan_id)


@router.patch(
    "/{loan_id}/return",
    response_model=LoanResponse,
    summary="Registrar devolución",
    description="Marca el préstamo como devuelto, registra la fecha y habilita el dispositivo.",
    responses={404: {"description": "Préstamo no encontrado."}, 409: {"description": "El préstamo ya fue devuelto."}},
)
def return_loan(loan_id: int, db: Session = Depends(get_db)):
    return loan_service.return_loan(db, loan_id)