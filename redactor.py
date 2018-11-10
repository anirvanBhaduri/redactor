"""
Redactor script.

The redactor script runs using a configuration
file. See the README for more instructions.

Author: Anirvan Bhaduri
Since: 10th Nov 2018
"""

import extract
import redact
import transform
import models

def run():
    """
    Run the redactor.

    This combines extract, redact and transform.
    """
    extract.run()
    redact.run()
    transform.run()

if __name__ == '__main__':
    run()
