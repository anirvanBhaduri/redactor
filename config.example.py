"""
An example config file.

Populate the below config variables as necessary.
"""

# strings to exclude during redaction
excludes = [
    "example_string"
]

# the string to replace redactable strings with
redaction_string = "[REDACTED]"

# sqlite file
sqlite_file = "store.db"

# google token file
# this file will be generated when the extractor is run
# i.e. when extract.py is run
google_token = "./credentials/token.json"

# google credentials file
# this should contain a set of credentials that allow
# the extract.py file to use Googles GMail API
google_credentials = "./credentials/credentials.json"

# google api scope
# the extractor only requires read access
google_scope = 'https://www.googleapis.com/auth/gmail.readonly'

# gmail api query to filter
gmail_query = ''

# store the important emails up to id
important_ids = 1000

# table column definitions
# used during transformation
# dbColumn to Table Header
table_columns = [
    ('example', "Example"), 
]

# FULL path to a folder that is the root for file generation
# tranform.py will generate files in this folder
generation_root = ''

# email type to transform
# email_type = 'Email'
email_type = 'RedactedEmail'
