"""Prepare data to be stored in by other process"""
from typing import List
from uuid import UUID
import json
import os

from fhir.resources.identifier import Identifier
from fhir.resources.patient import Patient
from sqlalchemy.orm import Session

from config.logger_config import setup_logger
from models.patient import PatientModel

LOGGER = setup_logger(__name__)


def item_exists(table: object, id, session: Session) -> bool:
    """Check if a record already exists in the database"""
    obj_from_db = session.query(table).filter_by(id=id).first()
    return obj_from_db is not None, obj_from_db


def compare_data(existing_obj, obj_data):
    existing_fields = set(existing_obj.__dict__.items())
    new_fields = set(obj_data.items())
    updated_fields = dict(new_fields - existing_fields)
    return updated_fields


def get_identifiers(identifiers: List[Identifier]) -> dict:
    for identifier in identifiers:
        display = identifier.type

        social_security_number = (
            identifier.value
            if display and display.text == 'Social Security Number'
            else None
        )

        drivers_license = (
            identifier.value
            if display and display.text == 'Driver\'s License'
            else None
        )

        passport_number = (
            identifier.value
            if display and display.text == 'Passport Number'
            else None
        )

    data = {
        'social_security_number': social_security_number,
        'drivers_license': drivers_license,
        'passport_number': passport_number
    }

    return data


def transform_data(path: str, session: Session) -> list:
    """Transform patient's data"""
    LOGGER.info(f'Loading Data from {path} folder')
    files = os.listdir(path)
    transformed_data = []

    with open(os.path.join(path, files[0]), 'r') as json_file:
        fhir_data = json.load(json_file)

        for entry in fhir_data.get('entry', []):
            resource = entry.get('resource', {})

            resource_type = resource.get('resourceType')
            if resource_type == 'Patient':
                patient = Patient.parse_obj(resource)

                identifiers = get_identifiers(patient.identifier)
                social_security_number = identifiers['social_security_number']
                drivers_license = identifiers['drivers_license']
                passport_number = identifiers['passport_number']

                # This resource is generally assumed to be active if no value
                # provided for the active element based on official FHIR docs
                active = patient.active if patient.active else True

                patient_data = {
                    'id': UUID(patient.id),
                    'active': active,
                    'gender': patient.gender,
                    'social_security_number': social_security_number,
                    'drivers_license': drivers_license,
                    'passport_number': passport_number,
                    'phone_number': patient.telecom[0].value,
                    'marital_status': patient.maritalStatus.text
                }

                obj_exists, existing_patient = item_exists(
                    PatientModel,
                    patient.id,
                    session
                )

                if obj_exists:
                    updated_data = compare_data(existing_patient, patient_data)
                    if updated_data:
                        # Update fields that have changed only
                        for field, value in updated_data.items():
                            setattr(existing_patient, field, value)
                        LOGGER.info(f'Updating patient: {patient.id}')
                        session.commit()
                else:
                    LOGGER.info(f'Adding new patient {patient.id}')
                    transformed_data.append(PatientModel(**patient_data))

    return transformed_data
