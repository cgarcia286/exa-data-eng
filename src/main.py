from sqlalchemy.orm import Session

from api.load import store_data_in_database
from api.transform import load_fhir_data
from config import BASE_DIR
from database.create_tables import create_tables

from database.db import engine

DATA_DIR = BASE_DIR / 'data'


def main():
    session = Session(engine)
    create_tables()
    parsed_data = load_fhir_data(DATA_DIR)
    store_data_in_database(session, parsed_data)


if __name__ == "__main__":
    main()
