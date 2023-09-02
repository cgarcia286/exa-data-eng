from sqlalchemy.orm import Session

from api.load import save_to_postgresql
from api.transform import transform_data
from config import BASE_DIR
from database.create_tables import create_tables

from database.db import engine


session = Session(engine)
if __name__ == "__main__":
    create_tables()
    transformed_data = transform_data(BASE_DIR / 'data', session)
    save_to_postgresql(transformed_data)
