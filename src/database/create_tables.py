from .db import engine
from .models.base import Base


def create_tables():
    """Create tables that do not exists"""
    Base.metadata.create_all(engine)
