# Redactor
A redactor that generates redacted content using
3 simple steps.

1. _Extract_ - extract and store the contents into a storage medium
2. _Redact_ - use a configuration to redact specified content
3. _Transform_ - generate redacted content and store into a storage medium

## Getting Started
Clone the repo.
```bash
git clone git@github.com:anirvanBhaduri/redactor.git
```

## Installing
Install pip.
```bash
sudo apt-get install python2-pip
```
Then install virtualenv using pip.
```bash
pip install virtualenv 
```
Create a virtualenv inside the cloned repo.
```bash
cd redactor/

virtualenv2 .virtualenv
```
Activate the virtualenv.
```bash
source .virtualenv/bin/activate
```
Install the requirements.
```bash
pip install -r requirements.txt
```
You can now run the script. To deactivate the virtualenv:
```bash
deactivate
```

## To use
Ensure you are in the root folder of the redactor repo.

Change the `config.example.py` file to `config.py` and edit
the config to personalise the script runtime.

Change the `example.store.db` file to the name you specify in the config.py
file for the `sqlite_file`. Then run the migration.
```bash
python migrate.py
```
This will display a verbose output of the tables it creates.

Then use
```bash
python redactor.py
```
to run the script.

## Built With
* [`python 2.7.13`](https://www.python.org/downloads/release/python-270/)

## Styling
* [PEP-8](https://www.python.org/dev/peps/pep-0008/#introduction) 
    - code styling
* [PEP-257](https://www.python.org/dev/peps/pep-0257/) 
    - documentation

## Authors
* _Anirvan Bhaduri_ - __Initial work__ 
    - [`anirvanBhaduri`](https://github.com/anirvanBhaduri)
