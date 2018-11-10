"""
The extract module.

Author: Anirvan Bhaduri
Since: 10th Nov 2018
"""

import config
import base64
import email

from googleapiclient import discovery
from httplib2 import Http
from oauth2client import client, tools
from oauth2client import file as ofile 
from apiclient import errors

def api_service():
    """
    Get the api service that will be used to extract the
    information for redaction.

    The api service method can be interchanged with a different
    service if a different service is required to get the redactable
    data.

    Returns:
    google_api_service
    """

    store = ofile.Storage(config.google_token)
    creds = store.get()

    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(
                        config.google_credentials, 
                        config.google_scope)

        creds = tools.run_flow(flow, store)

    return discovery.build('gmail', 'v1', http=creds.authorize(Http()))
    
class GMailExtractor(object):
    """
    The GMail Extractor.

    Used to extract emails using the token and 
    credentials configuration.
    """

    def __init__(self, service):
        """
        GMail Extractor constructor.

        Sets the service to be used to make calls to the Gmail
        API.
        """
        self._service = service

    def messages(self, user_id='me', query=''):
        """
        Extract a list of email ids using the gmail service.

        Args:
            user_id: (default 'me') The id of the user
            query: a special gmail query that can be used to
                filter the messages returned (i.e. emails)

        Returns:
            emails: list - a list of emails
        """
        try:
            response = self._service.users().messages() \
                            .list(userId=user_id, q=query).execute()

            messages = []
            if 'messages' in response:
                messages.extend(response['messages'])
                
            return messages

        except errors.HttpError as e:
            print(e) 
            return []

    def generate_email(self, mail_id, thread_id, user_id='me'):
        """
        Using the mail_id and thread_id, get all contents for the
        email and generate an Email model.

        Args:
            mail_id: the message id from gmail
            thread_id: the thread id from gmail

        Returns:
            Email: an email model
        """
        try:
            message = self._service.users().messages() \
                        .get(userId=user_id, 
                                id=mail_id).execute()

            # get the html content of the message
            for part in message['payload']['parts']:
                if 'text/html' in part['mimeType']:
                    body = base64.urlsafe_b64decode(
                            part['body']['data'].encode('ASCII'))
                    break


            return message
        except errors.HttpError as e:
            print(e)

def run():
    """
    Run extraction.
    """
    extractor = GMailExtractor(api_service())
    messages = extractor.messages()

    for message in messages:
        print(extractor.generate_email(
            message['id'], message['threadId']).keys())
        break

if __name__ == '__main__':
    run()
