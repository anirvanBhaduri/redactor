"""
The models module.

Contains models that interact with the database.

Author: Anirvan Bhaduri
Since: 10th Nov 2018
"""

import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime

# the base class for models to inherit
Base = declarative_base()

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
