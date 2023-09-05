import json

from sqlalchemy.orm import Session

from api.load import store_data_in_database
from api.transform import load_fhir_data
from config import BASE_DIR
from config.logger_config import setup_logger
from database.create_tables import create_tables
from database.db import engine


DATA_DIR = BASE_DIR / 'data'
LOGGER = setup_logger(__name__)


def main():
    session = Session(engine)
    create_tables()
    try:
        parsed_data = load_fhir_data(DATA_DIR)
    except (OSError, json.JSONDecodeError) as e:
        LOGGER.error(f'Error during FHIR data loading: {str(e)}')
        # Handle the error gracefully to prevent the program crashes
        parsed_data = []
    store_data_in_database(session, parsed_data)
    LOGGER.info('Process completed successfully!!!')


if __name__ == "__main__":
    main()
