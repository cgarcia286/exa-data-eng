from models.base import Base

from .db import engine


def create_tables():
    """Create tables that do not exists"""
    Base.metadata.create_all(engine)
