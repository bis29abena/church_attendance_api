from sqlmodel import create_engine, Session
from typing import Optional
from exceptions.env_exceptions import EnvironmentNotFound
import os

url: Optional[str] = os.getenv("DB_URL")

# check if there is an environment variable as this
if url:
    # create the engine
    engine = create_engine(
        url=url,
        connect_args={"check_same_thread": False},
        echo=True
    )
else:
    raise EnvironmentNotFound("DB_URL")

# create the get session to connect to the database
def get_session() -> Session:
    """Creates the session which will be use throughout the entire database

    Yields:
        Session(engine): yield the session upon every run
    """    
    with Session(engine) as session:
        yield session


def get_session_funct() -> Session:
    """Creates and returns a new session."""
    return Session(engine)