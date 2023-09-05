from uuid import UUID

from api.load import (
    _create_or_update_names,
    _create_or_update_patients,
    store_data_in_database
)
from database.models.patient import PatientModel, HumanNameModel, AddressModel


def test_store_data_in_database(db_session):
    names = [
        {
            'patient_id': '53447e34-ade0-4963-86d7-aa081978ea6d',
            'use': 'official',
            'given': 'John',
            'family': 'Doe',
            'prefix': 'Mr.',
            'suffix': None
        }
    ]
    addresses = [
        {
            'patient_id': '53447e34-ade0-4963-86d7-aa081978ea6d',
            'use': None,
            'type': None,
            'line': '859 Altenwerth Run Unit 88',
            'city': 'Charlton',
            'district': None,
            'state': 'MA',
            'postal_code': None,
            'country': 'US'
        }
    ]

    patient_data = [
        {
            'id': UUID('53447e34-ade0-4963-86d7-aa081978ea6d'),
            'names': names,
            'addresses': addresses
        }
    ]

    store_data_in_database(db_session, patient_data)

    patient: PatientModel = db_session.query(PatientModel).first()
    assert patient is not None
    assert str(patient.id) == '53447e34-ade0-4963-86d7-aa081978ea6d'

    name: HumanNameModel = patient.names[0]
    assert len(patient.names) == 1
    assert str(name.patient_id) == '53447e34-ade0-4963-86d7-aa081978ea6d'
    assert name.use.value == 'official'
    assert name.family == 'Doe'
    assert name.given == 'John'
    assert name.prefix == 'Mr.'
    assert name.suffix is None

    address: AddressModel = patient.addresses[0]
    assert len(patient.addresses) == 1
    assert str(address.patient_id) == '53447e34-ade0-4963-86d7-aa081978ea6d'
    assert address.use is None
    assert address.type is None
    assert address.line == '859 Altenwerth Run Unit 88'
    assert address.city == 'Charlton'
    assert address.district is None
    assert address.state == 'MA'
    assert address.postal_code is None
    assert address.country == 'US'


def test_create_or_update_patients_create_new_patient(db_session):
    patient_data = {
        'id': UUID('53447e34-ade0-4963-86d7-aa081978ea6d'),
        'active': True,
        'gender': 'male',
        'social_security_number': '123-45-6789',
        'drivers_license': 'DL12345',
        'phone_number': '123-456-7890',
        'marital_status': 'Single',
    }

    patient = _create_or_update_patients(db_session, patient_data)

    assert patient is not None
    assert str(patient.id) == '53447e34-ade0-4963-86d7-aa081978ea6d'
    assert patient.active
    assert patient.gender == 'male'
    assert patient.social_security_number == '123-45-6789'
    assert patient.drivers_license == 'DL12345'
    assert patient.marital_status == 'Single'
    assert patient.phone_number == '123-456-7890'


def test_create_or_update_patients_update_existing_patient(db_session):
    patient_data = {
        'id': UUID('53447e34-ade0-4963-86d7-aa081978ea6d'),
        'active': True,
        'gender': 'male',
        'social_security_number': '123-45-6789',
        'drivers_license': 'DL12345',
        'phone_number': '123-456-7890',
        'marital_status': 'Single',
    }

    _create_or_update_patients(db_session, patient_data)

    updated_data = {
        'id': UUID('53447e34-ade0-4963-86d7-aa081978ea6d'),
        'active': True,
        'gender': 'male',
        'social_security_number': '123-45-7777',
        'drivers_license': 'DL12345',
        'phone_number': '123-456-7890',
        'marital_status': 'Single',
    }

    patient = _create_or_update_patients(db_session, updated_data)
    assert patient.social_security_number == '123-45-7777'


def test_create_or_update_names(db_session):
    patient = PatientModel(
        id='53447e34-ade0-4963-86d7-aa081978ea6d',
    )
    db_session.add(patient)
    db_session.commit()

    names = [
        {
            'patient_id': '53447e34-ade0-4963-86d7-aa081978ea6d',
            'use': 'official',
            'given': 'John',
            'family': 'Doe',
            'prefix': 'Mr.',
            'suffix': None
        }
    ]

    _create_or_update_names(db_session, patient, names)

    name = db_session.query(
        HumanNameModel
    ).filter_by(
        patient_id=patient.id
    ).first()

    assert name is not None
    assert str(name.patient_id) == '53447e34-ade0-4963-86d7-aa081978ea6d'
    assert name.given == 'John'
    assert name.family == 'Doe'
    assert name.use.value == 'official'
    assert name.prefix == 'Mr.'
    assert name.suffix is None
