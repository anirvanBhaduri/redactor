"""
Run migrations to create models.
"""
import os
import config
import models
from sqlalchemy import create_engine, Index
from sqlalchemy.orm import sessionmaker

# file's directory
PWD = os.path.dirname(os.path.realpath(__file__))

# create the engine
engine = create_engine(
            'sqlite:///{}/{}'.format(PWD, config.sqlite_file),
            echo=True)

# migrate the db tables
models.Base.metadata.create_all(engine)

# add index for external_id
external_id_index = Index('external_id_index', models.Email.external_id)
external_id_index.create(bind=engine)
