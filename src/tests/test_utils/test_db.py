from database.models.patient import PatientModel

from utils.db import sqlalchemy_uri_generator, compare_data


def test_sqlalchemy_uri_generator():
    db_user = 'test_user'
    db_password = 'test_password'
    db_host = 'localhost'
    db_name = 'test_db'

    result = sqlalchemy_uri_generator(db_user, db_password, db_host, db_name)

    expected = f'postgresql://{db_user}:{db_password}@{db_host}/{db_name}'
    assert result == expected


def test_compare_data(db_session):
    existing_obj = PatientModel(
        id='53447e34-ade0-4963-86d7-aa081978ea6d',
        gender='male'
    )
    db_session.add(existing_obj)
    obj_data = {'gender': 'female'}

    updated_fields = compare_data(existing_obj, obj_data)

    expected_updated_fields = {'gender': 'female'}
    assert updated_fields == expected_updated_fields
