"""
Redactor script.

The redactor script runs using a configuration
file. See the README for more instructions.

Author: Anirvan Bhaduri
Since: 10th Nov 2018
"""

import os
import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# file's directory
PWD = os.path.dirname(os.path.realpath(__file__))

# create the engine
engine = create_engine(
            'sqlite:///{}/{}'.format(PWD, config.sqlite_file), 
            echo=True)

# create a db session
Session = sessionmaker(bind=engine)
session = Session()

def run():
    """
    Run the redactor.
    """
    pass

if __name__ == '__main__':
    run()
