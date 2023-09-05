"""Save transformed data into PostgreSQL"""
from typing import List

from sqlalchemy.orm import Session

from config.logger_config import setup_logger
from database.models.patient import AddressModel, HumanNameModel, PatientModel
from utils.db import compare_data, item_exists

LOGGER = setup_logger(__name__)


def store_data_in_database(session: Session, parsed_data: List[dict]):
    """
    Stores patient data in a database using an SQLAlchemy session.

    :param Session session: An active SQLAlchemy session for interacting with
    the database.
    :param List[dict] parsed_data: A list of dictionaries containing patient
    data to be stored.

    The function takes an active SQLAlchemy session and a list of dictionaries
    representing patient data.

    For each patient data dictionary, names and addresses are extracted, and
    then a patient entry is created or updated in the database using the
    '_create_or_update_patients' function. Subsequently, name and address
    entries associated with that patient are created or updated using the
    '_create_or_update_names' and '_create_or_update_addresses' functions.
    """
    with session:
        for patient_data in parsed_data:
            names = patient_data.pop('names')
            addresses = patient_data.pop('addresses')

            patient: PatientModel = _create_or_update_patients(
                session,
                patient_data
            )
            _create_or_update_names(session, patient, names)
            _create_or_update_addresses(session, patient, addresses)


def _create_or_update_patients(
    session: Session,
    patient_data: dict
) -> PatientModel:
    """
    Creates or updates patient data in the DB using an SQLAlchemy session.

    :param Session session: An active SQLAlchemy session for interacting with
    the database.
    :param dict patient_data: A dictionary containing patient data to be
    created or updated.

    :return PatientModel: The created or updated PatientModel instance.

    This function checks if a patient with the specified ID exists in the DB.
    If the patient exists, it compares the existing data with the provided
    argument 'patient_data' and updates the fields that have changed. If the
    patient does not exist, a new patient is added to the database with the
    provided argument 'patient_data'.
    """
    obj_exists, patient = item_exists(
        PatientModel,
        patient_data['id'],
        session
    )

    if obj_exists:
        updated_data = compare_data(patient, patient_data)
        if updated_data:
            for field, value in updated_data.items():
                setattr(patient, field, value)
            LOGGER.info(f'Updating patient: {patient_data["id"]}')
            session.commit()
    else:
        LOGGER.info(f'Adding new patient {patient_data["id"]}')
        new_patient = PatientModel(**patient_data)
        session.add(new_patient)
        session.commit()
        patient = new_patient

    return patient


def _create_or_update_names(
    session: Session,
    patient: PatientModel,
    names: list
):
    """
    Creates or updates names associated with a patient in the database using an
    SQLAlchemy session.

    :param Session session: An active SQLAlchemy session for interacting with
    the database.
    :param PatientModel patient: The PatientModel instance to which the names
    are associated.
    :param list names: List of patient names to be created or updated.

    This function iterates through the provided list of names for a patient,
    checks if each name already exists in the database based on the patient's
    ID, and either adds a new name or updates an existing one. The function
    compares the provided name data with the existing name data and updates
    any changed fields.
    """
    existing_names = session.query(
        HumanNameModel
    ).filter_by(patient_id=patient.id).all()

    # Create a set of existing names for efficient lookup
    existing_names_set = set(
        (name.family, name.given, name.use.value) for name in existing_names
    )

    new_names = []
    for name_data in names:
        name_key = (name_data['family'], name_data['given'], name_data['use'])

        if name_key not in existing_names_set:
            LOGGER.info(f'Adding new name for patient {patient.id}')
            new_names.append(HumanNameModel(**name_data))
            existing_names_set.add(name_key)

    # Add all new names to the patient's names relationship
    patient.names.extend(new_names)

    # Commit the changes to the database
    session.commit()


def _create_or_update_addresses(
    session: Session,
    patient: PatientModel,
    addresses: list
):
    """
    Creates or updates addresses associated with a patient in the database
    using an SQLAlchemy session.

    :param Session session: An active SQLAlchemy session for interacting with
    the database.
    :param PatientModel patient: The PatientModel instance to which the
    addresses are associated.
    :param list addresses: A list of addresses to be created or updated.

    This function iterates through the provided list of addresses for a
    patient, checks if each address already exists in the database based on the
    patient's ID, and either adds a new address or updates an existing one. The
    function compares the provided address data with the existing address data
    and updates any changed fields.
    """
    existing_addresses = session.query(
        AddressModel
    ).filter_by(patient_id=patient.id).all()

    for address_data in addresses:
        address_exists = any(
            a.line == address_data['line'] and
            a.city == address_data['city'] and
            a.use == address_data['use']
            for a in existing_addresses
        )

        if not address_exists:
            LOGGER.info(f'Adding new address for patient {patient.id}')
            new_address = AddressModel(**address_data)
            patient.addresses = [new_address]
            session.commit()

        # TODO: Implementation for Update on change
