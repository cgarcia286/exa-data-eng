"""Prepare data to be stored in by other process"""
from typing import List
from uuid import UUID
import json
import os

from fhir.resources.address import Address
from fhir.resources.humanname import HumanName
from fhir.resources.identifier import Identifier
from fhir.resources.patient import Patient
from sqlalchemy.orm import Session

from config.logger_config import setup_logger
from models.patient import AddressModel, HumanNameModel, PatientModel

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
    # files = os.listdir(path)
    transformed_data = []

    for filename in os.listdir(path):
        if filename.endswith(".json"):
            with open(os.path.join(path, filename), "r") as json_file:
                fhir_data = json.load(json_file)

    # with open(os.path.join(path, files[0]), 'r') as json_file:
    #     fhir_data = json.load(json_file)

            for entry in fhir_data.get('entry', []):
                resource = entry.get('resource', {})

                resource_type = resource.get('resourceType')
                if resource_type == 'Patient':
                    patient = Patient.parse_obj(resource)

                    # Es una lista!
                    # language = patient.communication[0].language.text
                    identifiers = get_identifiers(patient.identifier)
                    social_security_number = identifiers['social_security_number']
                    drivers_license = identifiers['drivers_license']
                    passport_number = identifiers['passport_number']

                    # This resource is generally assumed to be active if no value is
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

                    obj_exists, existing_patient = item_exists(PatientModel, patient.id, session)
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

                    names: List[HumanName] = patient.name
                    for name in names:
                        # This elements can have multiple values or to be null
                        given = ' '.join(name.given) if name.given else None
                        prefix = ' '.join(name.prefix) if name.prefix else None
                        suffix = ' '.join(name.suffix) if name.suffix else None

                        name_data = {
                            'patient_id': UUID(patient.id),
                            'use': name.use,
                            'given': given,
                            'family': name.family,
                            'prefix': prefix,
                            'suffix': suffix
                        }

                        existing_names = session.query(
                            HumanNameModel
                        ).filter_by(patient_id=patient.id).all()

                        name_exists = any(
                            n.family == name_data['family'] and
                            n.given == name_data['given'] and
                            n.use.value == name_data['use']
                            for n in existing_names
                        )

                        if not name_exists:
                            LOGGER.info(f'Adding new name for patient {patient.id}')
                            transformed_data.append(HumanNameModel(**name_data))
                        else:
                            # Update name only if given or family name changed
                            name_to_update = session.query(HumanNameModel).filter_by(
                                patient_id=patient.id,
                                given=name_data['given'],
                                family=name_data['family']
                            ).first()
                            name_to_update.use = name_to_update.use.value

                            updated_fields = compare_data(name_to_update, name_data)
                            if updated_fields:
                                for field, value in updated_fields.items():
                                    setattr(name_to_update, field, value)
                                LOGGER.info(f'Updating name: {name_to_update.id}')
                                session.commit()

                    addresses: List[Address] = patient.address
                    for address in addresses:
                        address_data = {
                            'patient_id': UUID(patient.id),
                            'use': address.use,
                            'type': address.type,
                            'line': ' '.join(address.line),
                            'city': address.city,
                            'district': address.district,
                            'state': address.state,
                            'postal_code': address.postalCode,
                            'country': address.country
                        }

                        existing_addresses = session.query(
                            AddressModel
                        ).filter_by(patient_id=patient.id).all()

                        address_exists = any(
                            a.line == address_data['line'] and
                            a.city == address_data['city'] and
                            a.use == address_data['use']
                            for a in existing_addresses
                        )

                        if not address_exists:
                            LOGGER.info(f'Adding new address for patient {patient.id}')
                            transformed_data.append(AddressModel(**address_data))

                        # TODO: Implementation for Update on change

    return transformed_data
