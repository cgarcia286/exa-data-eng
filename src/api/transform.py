"""Prepare data to be stored by another process"""
from typing import List
from uuid import UUID
import json
import os

from fhir.resources.address import Address
from fhir.resources.humanname import HumanName
from fhir.resources.identifier import Identifier
from fhir.resources.patient import Patient

from config.logger_config import setup_logger
from models.patient import AddressModel, HumanNameModel, PatientModel

LOGGER = setup_logger(__name__)


def load_fhir_data(path: str):
    LOGGER.info(f'Loading Data from {path} directory')
    transformed_data = []

    for filename in os.listdir(path):
        if filename.endswith(".json"):
            with open(os.path.join(path, filename), "r") as json_file:
                fhir_data = json.load(json_file)
                transformed_data.extend(parse_fhir_data(fhir_data))

    return transformed_data


def parse_fhir_data(fhir_data: json) -> list:
    parsed_data = []

    for entry in fhir_data.get('entry', []):
        resource = entry.get('resource', {})
        resource_type = resource.get('resourceType')

        if resource_type == 'Patient':
            patient = Patient.parse_obj(resource)
            parsed_data.append(parse_patient_data(patient))

    return parsed_data


def parse_patient_data(patient: Patient) -> dict:
    """
    _summary_

    :param Patient patient: _description_

    :return dict: _description_
    """
    identifiers = _get_identifiers(patient.identifier)
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
        'marital_status': patient.maritalStatus.text,
    }

    patient_instance = PatientModel(**patient_data)

    names_data = parse_patient_names(patient, patient.name)
    human_names = [HumanNameModel(**name) for name in names_data]
    patient_instance.names = human_names

    addresses_data = parse_patient_addresses(
        patient,
        patient.address
    )
    addresses = [AddressModel(**address) for address in addresses_data]
    patient_instance.addresses = addresses

    patient_data.update({
        'names': human_names,
        'addresses': addresses
    })

    return patient_data


def parse_patient_names(patient: Patient, names: List[HumanName]) -> dict:
    """
    _summary_

    :param Patient patient: _description_
    :param List[HumanName] names: _description_

    :return dict: _description_
    """
    parsed_patient_names = []

    for name in names:
        # These elements can have multiple values ​​or be null
        given = ' '.join(name.given) if name.given else None
        prefix = ' '.join(name.prefix) if name.prefix else None
        suffix = ' '.join(name.suffix) if name.suffix else None

        name_data = {
            'patient_id': UUID(patient.id),
            'use': name.use,
            'given': given[:-3],
            'family': name.family[:-3],
            'prefix': prefix,
            'suffix': suffix
        }

        parsed_patient_names.append(name_data)

    return parsed_patient_names


def parse_patient_addresses(
    patient: Patient,
    addresses: List[Address]
) -> dict:
    """
    _summary_

    :param Patient patient: _description_
    :param List[Address] addresses: _description_

    :return dict: _description_
    """
    parsed_patient_addresses = []

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

        parsed_patient_addresses.append(address_data)

    return parsed_patient_addresses


def _get_identifiers(identifiers: List[Identifier]) -> dict:
    """
    _summary_

    :param List[Identifier] identifiers: _description_
    :return dict: _description_
    """
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
