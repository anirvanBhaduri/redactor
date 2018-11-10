"""
The models module.

Contains models that interact with the database.

Author: Anirvan Bhaduri
Since: 10th Nov 2018
"""

import os
import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime

# file's directory
PWD = os.path.dirname(os.path.realpath(__file__))

# create the engine
engine = create_engine('sqlite:///{}/{}'.format(PWD, config.sqlite_file))

# create a db session
Session = sessionmaker(bind=engine)
session = Session()

# the base class for models to inherit
Base = declarative_base()

def db_session():
    """
    Get a db session.
    """
    return session

def db_engine():
    """
    Get the db engine.
    """
    return engine

class Email(Base):
    """
    The Email model. Stores emails.
    """
    __tablename__ = 'emails'

    id = Column(Integer, primary_key=True)
    subject = Column(String)
    email_from = Column(String)
    email_to = Column(String)
    time = Column(DateTime)
    body = Column(String)

class RedactedEmail(Base):
    """
    The Redacted Email model. Stores redacted emails.
    """
    __tablename__ = 'redacted_emails'

    id = Column(Integer, primary_key=True)
    subject = Column(String)
    email_from = Column(String)
    email_to = Column(String)
    time = Column(DateTime)
    body = Column(String)
