"""Helper functions to use with Database"""
from uuid import UUID

from sqlalchemy.orm import Session


def sqlalchemy_uri_generator(
    username: str,
    password: str,
    host: str,
    db_name: str,
    driver: str = 'postgresql'
) -> str:
    """
    Build the database URI from params
    """
    return f'{driver}://{username}:{password}@{host}/{db_name}'


def item_exists(table: object, id: UUID, session: Session) -> tuple:
    """
    Check if a record already exists in the database.

    :param object table: The SQLAlchemy model class to check.
    :param UUID id: The ID of the record to check.
    :param Session session: The SQLAlchemy session.

    :return tuple: A tuple indicating whether the record exists and the
    existing record if exists.
    """
    assert isinstance(id, UUID)
    obj_from_db = session.query(table).filter_by(id=id).first()
    return obj_from_db is not None, obj_from_db


def compare_data(existing_obj: dict, obj_data: dict) -> dict:
    """
    Compare data between an existing object and new data.

    :param dict existing_obj: The existing object's data.
    :param dict obj_data: The new data to compare.

    :return dict: A dictionary containing fields that have changed.
    """
    existing_fields = set(existing_obj.__dict__.items())
    new_fields = set(obj_data.items())
    updated_fields = dict(new_fields - existing_fields)
    return updated_fields
