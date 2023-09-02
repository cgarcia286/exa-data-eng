"""Save transformed data to PostgreSQL"""
from sqlalchemy.orm import sessionmaker

from database.db import engine


def save_to_postgresql(data):
    Session = sessionmaker(bind=engine)

    with Session() as session:
        for item in data:
            session.add(item)
        session.commit()
