"""
Run migrations to create models.
"""

import os
import config
from sqlalchemy import create_engine

# file's directory
PWD = os.path.dirname(os.path.realpath(__file__))

# create the engine
engine = create_engine(
            'sqlite:///{}/{}'.format(PWD, config.sqlite_file), 
            echo=True)

import models

# migrate the db tables
models.Base.metadata.create_all(engine)
