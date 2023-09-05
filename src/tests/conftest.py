from unittest.mock import patch, mock_open
import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest

from database.models.base import Base
from database.models.patient import PatientModel

DATABASE_URL = "postgresql://exa-data:exa-data@db.test/exa-data-test"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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
    # Creates a sample Patient object with basic attributes
    return PatientModel(
        id='53447e34-ade0-4963-86d7-aa081978ea6d',
        names=[],
        addresses=[]
    )


# Configure the testing database
@pytest.fixture(scope='function')
def db_session():
    # Establishes a connection to the test database
    connection = engine.connect()

    # Create tables if does not exist
    Base.metadata.create_all(engine)

    # Create a top-level transaction for testing
    transaction = connection.begin()

    # Create SQLAlchemy session for testing
    session = SessionLocal(bind=connection)

    # Provides test session
    try:
        yield session
    finally:
        # Clean after DB each test
        session.close()
        transaction.rollback()
        connection.close()
