"""Model for Patient table"""
from uuid import uuid4

from sqlalchemy import Boolean, Column, String, UUID

from .base import TimeStampModel


class PatientModel(TimeStampModel):
    __tablename__ = 'patients'

    id = Column(UUID, primary_key=True, index=True, default=uuid4)
    active = Column(Boolean, default=True)
    social_security_number = Column(String)
    drivers_license = Column(String)
    passport_number = Column(String)
    gender = Column(String)
    phone_number = Column(String)
    marital_status = Column(String)

    def __repr__(self):
        full_name = f'{self.names[0]}' if self.names else 'Unknown'
        return f'Patient(id={self.id}, full_name={full_name})'
