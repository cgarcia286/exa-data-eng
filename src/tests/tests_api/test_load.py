from api.load import store_data_in_database
from database.models.patient import PatientModel


def test_store_data_in_database(db):
    patient_data = [
        {
            'id': '630aa848-8a38-4730-9319-5a80e798b48d',
            'names': [{'given': 'John', 'family': 'Doe'}],
            'addresses': [{'city': 'City1'}],
        },
        {
            'id': '1d6cac1c-0f8f-4c59-bc63-f0f7c7a671e6',
            'names': [{'given': 'Alice', 'family': 'Smith'}],
            'addresses': [{'city': 'City2'}],
        },
    ]

    store_data_in_database(db, patient_data)

    assert db.query(PatientModel).count() == 2
