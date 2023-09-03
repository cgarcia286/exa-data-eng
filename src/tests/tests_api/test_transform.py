from unittest.mock import patch
from uuid import UUID
import json

from fhir.resources.patient import Patient
from fhir.resources.address import Address
from fhir.resources.identifier import Identifier
import pytest

from api.transform import (
    _get_identifiers,
    load_fhir_data,
    parse_fhir_data,
    parse_patient_addresses,
    parse_patient_data,
    parse_patient_names,
)
from database.models.patient import HumanNameModel


def test_load_fhir_data(mock_os_listdir, mock_json_load):
    result = load_fhir_data('/fake/directory')

    # Verify that the result contains the sample JSON data
    assert len(result) == 2


def test_load_fhir_data_os_error(mock_os_listdir):
    with patch('builtins.open', side_effect=OSError('Test OSError')):
        with pytest.raises(OSError):
            load_fhir_data('/fake/directory')


def test_load_fhir_data_json_decode_error(
    mock_os_listdir,
    mock_json_load,
    caplog
):
    with patch(
        'json.load',
        side_effect=json.JSONDecodeError('Test JSONDecodeError', '', 0)
    ):
        load_fhir_data('/fake/directory')

    assert 'Error decoding JSON in file' in caplog.text


def test_parse_fhir_data(sample_fhir_data):
    parsed_data = parse_fhir_data(sample_fhir_data)
    assert len(parsed_data) == 1

    data = parsed_data[0]
    assert 'id' in data
    assert 'active' in data
    assert 'gender' in data

    assert str(data['id']) == '53447e34-ade0-4963-86d7-aa081978ea6d'
    assert data['active']
    assert data['gender'] == 'male'
    assert data['social_security_number'] is None
    assert data['drivers_license'] == 'DL12345'
    assert data['passport_number'] is None
    assert data['phone_number'] == '123-456-7890'
    assert data['marital_status'] == 'Single'


def test_parse_patient_data(sample_fhir_data):
    patient = Patient.parse_obj(sample_fhir_data['entry'][0]['resource'])
    parsed_patient_data = parse_patient_data(patient)
    assert 'id' in parsed_patient_data
    assert 'active' in parsed_patient_data
    assert 'gender' in parsed_patient_data
    assert 'social_security_number' in parsed_patient_data


def test_parse_patient_names(sample_patient):
    sample_names = [
        HumanNameModel(
            patient_id=sample_patient.id,
            use='official',
            given=['John123'],
            family='Doe456',
            prefix=None,
            suffix=None
        )
    ]

    result = parse_patient_names(sample_patient, sample_names)

    expected_result = [{
        'patient_id': UUID(sample_patient.id),
        'use': 'official',
        'given': 'John',
        'family': 'Doe',
        'prefix': None,
        'suffix': None
    }]

    assert result == expected_result


def test_parse_patient_addresses(sample_patient):
    sample_addresses = [
        Address(
            use='home',
            type='physical',
            line=['123 Main St'],
            city='Springfield',
            district='Shelby',
            state='NY',
            postalCode='12345',
            country='USA'
        )
    ]

    result = parse_patient_addresses(sample_patient, sample_addresses)

    expected_result = [{
        'patient_id': UUID(sample_patient.id),
        'use': 'home',
        'type': 'physical',
        'line': '123 Main St',
        'city': 'Springfield',
        'district': 'Shelby',
        'state': 'NY',
        'postal_code': '12345',
        'country': 'USA'
    }]

    assert result == expected_result


def test_get_identifiers():
    # Create a list of Sample Identifier instances for the test
    identifiers = [
        Identifier(
            value="123456",
            type={
                'coding': [{'display': 'Social Security Number'}],
                'text': 'Social Security Number'
            }
        )
    ]

    result = _get_identifiers(identifiers)

    expected_result = {
        'social_security_number': "123456",
        'drivers_license': None,
        'passport_number': None
    }

    assert result == expected_result
