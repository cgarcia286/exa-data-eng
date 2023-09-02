"""Save transformed data into PostgreSQL"""
from sqlalchemy.orm import Session

from config.logger_config import setup_logger
from models.patient import AddressModel, HumanNameModel, PatientModel
from utils.db import compare_data, item_exists

LOGGER = setup_logger(__name__)


def store_data_in_database(session: Session, parsed_data: list):
    """
    Store parsed Fast Healthcare Interoperability Resources (FHIR) data in
    the database.

    :param Session session: The SQLAlchemy session.
    :param list parsed_data: List of parsed data to store.
    """
    with session:
        for patient_data in parsed_data:
            # Compare and update patients if exists otherwise, create a new one
            names = patient_data.pop('names')
            adresses = patient_data.pop('adresses')

            obj_exists, existing_patient = item_exists(
                PatientModel,
                patient_data['id'],
                session
            )
            if obj_exists:
                updated_data = compare_data(existing_patient, patient_data)
                if updated_data:
                    # Update fields that have changed only
                    for field, value in updated_data.items():
                        setattr(existing_patient, field, value)
                    LOGGER.info(f'Updating patient: {patient_data["id"]}')
                    session.commit()
            else:
                LOGGER.info(f'Adding new patient {patient_data["id"]}')
                new_patient = PatientModel(**patient_data)
                session.add(new_patient)
                session.commit()

            patient = existing_patient or new_patient

            # Compare and update names if exists otherwise, create a new one
            for name in names:
                name.__dict__.pop('patient')
                name.__dict__.pop('_sa_instance_state')
                name_data = name.__dict__

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
                    session.add(HumanNameModel(**name_data))
                    session.commit()

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

            # Compare and update addresses if exists otherwise, create a new one
            for address in adresses:
                address.__dict__.pop('patient')
                address.__dict__.pop('_sa_instance_state')
                address_data = address.__dict__

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
                    session.add(AddressModel(**address_data))
                    session.commit()

                # TODO: Implementation for Update on change
