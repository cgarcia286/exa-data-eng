from unittest.mock import patch, mock_open
import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest

from database.models.base import Base
from database.models.patient import PatientModel


@pytest.fixture
def mock_os_listdir():
    # Fixture to patch os.listdir
    with patch('os.listdir', return_value=['file1.json', 'file2.json']):
        yield


@pytest.fixture
def sample_fhir_data():
    # Create a dictionary with sample data in FHIR format to use in testing
    return {
        'entry': [
            {
                'resource': {
                    'resourceType': 'Patient',
                    'id': '53447e34-ade0-4963-86d7-aa081978ea6d',
                    'active': True,
                    'gender': 'male',
                    'identifier': [
                        {
                            'type': {'text': 'Social Security Number'},
                            'value': '123-45-6789',
                        },
                        {
                            'type': {'text': 'Driver\'s License'},
                            "value": "DL12345",
                        },
                    ],
                    'telecom': [{'value': '123-456-7890'}],
                    'maritalStatus': {'text': 'Single'},
                    'name': [
                        {
                            'use': 'official',
                            'given': ['John123'],
                            'family': 'Doe456',
                            'prefix': ['Mr.'],
                            'suffix': ['Jr.'],
                        }
                    ],
                    'address': [
                        {
                            'use': 'home',
                            'type': 'both',
                            'line': ['123 Main St'],
                            'city': 'Cityville',
                            'district': 'Districtville',
                            'state': 'ST',
                            'postalCode': '12345',
                            'country': 'US',
                        }
                    ],
                }
            }
        ]
    }


@pytest.fixture
def mock_json_load(sample_fhir_data):
    with patch(
        'builtins.open',
        mock_open(read_data=json.dumps(sample_fhir_data))
    ):
        yield


@pytest.fixture
def sample_patient():
    # Creates a sample Patient object with attributes necessary for the test
    return PatientModel(
        id='53447e34-ade0-4963-86d7-aa081978ea6d',
        names=[],
        addresses=[]
    )


# TODO: Change db engine with posgresql
# Configure the in-memory database (SQLite) for testing
@pytest.fixture(scope="module")
def db():
    engine = create_engine('sqlite:///:memory:')
    Session = sessionmaker(bind=engine)
    session = Session()

    Base.metadata.create_all(engine)
    yield session

    # Log off and delete the in-memory database
    session.close()
    engine.dispose()
