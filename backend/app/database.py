import os
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session


def database_url():
    url = make_url(os.environ["DATABASE_URL"])
    if url.drivername == "postgresql":
        url = url.set(drivername="postgresql+psycopg")
    return url


@lru_cache
def get_engine():
    return create_engine(database_url(), pool_pre_ping=True)


def get_session():
    with Session(get_engine()) as session:
        yield session
