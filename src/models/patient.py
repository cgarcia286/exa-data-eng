"""Model for Patient table"""
from uuid import uuid4

from enum import Enum as PythonEnum
from sqlalchemy import Boolean, Column, Enum, ForeignKey, String, UUID
from sqlalchemy.orm import relationship

from .base import TimeStampModel


class HumanNameUse(PythonEnum):
    usual = 'usual'
    official = 'official'
    temp = 'temp'
    nickname = 'nickname'
    anonymous = 'anonymous'
    old = 'old'
    maiden = 'maiden'


class HumanNameModel(TimeStampModel):
    __tablename__ = 'human_names'

    id = Column(UUID, primary_key=True, index=True, default=uuid4)
    patient_id = Column(UUID, ForeignKey('patients.id'))
    use = Column(Enum(HumanNameUse))
    given = Column(String, index=True)
    family = Column(String, index=True)
    prefix = Column(String)
    suffix = Column(String)

    # Establish the inverse relationship with the Patients table
    patient = relationship('PatientModel', back_populates='names')

    def __repr__(self):
        return f'{self.given} {self.family}'


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

    # One-to-many relationship with patient name table
    names = relationship('HumanNameModel', back_populates='patient')

    # One-to-many relationship with patient address table
    addresses = relationship('AddressModel', back_populates='patient')

    def __repr__(self):
        full_name = f'{self.names[0]}' if self.names else 'Unknown'
        return f'Patient(id={self.id}, full_name={full_name})'


class AddressUse(PythonEnum):
    home = 'home'
    work = 'work'
    temp = 'temp'
    old = 'old'
    billing = 'billing'


class AddressModel(TimeStampModel):
    __tablename__ = 'addresses'

    id = Column(UUID, primary_key=True, index=True, default=uuid4)
    patient_id = Column(UUID, ForeignKey('patients.id'))
    use = Column(String)
    type = Column(String)
    line = Column(String)
    city = Column(String)
    district = Column(String)
    state = Column(String)
    postal_code = Column(String)
    country = Column(String)

    # Establish the inverse relationship with the Patients table
    patient = relationship('PatientModel', back_populates='addresses')

    def __repr__(self):
        return f'Address(id={self.id})'
