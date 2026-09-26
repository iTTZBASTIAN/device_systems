from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Index
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Loan(Base):
    __tablename__ = "loans"
    __table_args__ = (
        Index("ix_loans_user_device", "user_id", "device_id"),
        Index("ix_loans_status_loan_date", "status", "loan_date"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="RESTRICT"), nullable=False, index=True)
    loan_date = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=False,
        index=True,
    )
    return_date = Column(DateTime, nullable=True)
    status = Column(String, nullable=False, default="active", index=True)

    user = relationship("User", back_populates="loans")
    device = relationship("Device", back_populates="loans")