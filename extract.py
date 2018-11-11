"""
The extract module.

Author: Anirvan Bhaduri
Since: 10th Nov 2018
"""

import config
import base64
import email
import models

from datetime import datetime
from dateutil.parser import parse
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
    _page_token = None

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
            if self.page_token():
                response = self._service.users().messages() \
                                .list(userId=user_id, q=query,
                                        pageToken=self.page_token()).execute()
            else:
                response = self._service.users().messages() \
                                .list(userId=user_id, q=query).execute()

            messages = []
            if 'messages' in response:
                messages.extend(response['messages'])

            self._page_token = response.get('nextPageToken')
            return messages

        except errors.HttpError as e:
            print(e) 
            return []

    def page_token(self):
        """
        Get the GMail api page token for the next page
        in the extractor query.

        Returns:
            page_token: string - a token to gather the next page
                of the query.
        """
        return self._page_token

    def retrieve_from_parts(self, parts):
        """
        Get the part which represents the body of the GMail
        message.

        Args:
            parts: list - a list of message parts

        Returns:
            content: the body material
        """
        mimes = {
            "text/plain": "", 
            "text/html": ""
        }

        # we only want plain text or html
        # we don't care about the other parts
        for part in parts:
            if mimes.get(part['mimeType'].strip()) is not None:
                mimes[part['mimeType']] = part['body'].get('data')

        if mimes.get('text/html'):
            return mimes['text/html']

        return mimes['text/plain']

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
            # dict to gather email information
            meta = {
                "Subject": True,
                "From": True,
                "To": True,
                "Date": True,
            }

            message = self._service.users().messages() \
                        .get(userId=user_id, 
                                format='full',
                                id=mail_id).execute()

            # lets check the partId of the actual content
            mime = message['payload']['mimeType']

            if mime.startswith('multipart'):
                content = self.retrieve_from_parts(
                            message['payload']['parts'])
            else:
                content = message['payload']['body']['data']

            # don't continue to make email if no content
            if not content:
                return

            body = base64.urlsafe_b64decode(
                        content.encode('ASCII'))

            for header in message['payload']['headers']:
                if meta.get(header['name'], False):
                    meta[header['name'].lower()] = header['value']

                    del meta[header['name']]

            # gmail provides the internal date as epoch ms
            date = datetime.fromtimestamp(
                        float(message['internalDate']) / 1000)

            return models.Email(
                        external_id=message['id'],
                        thread_id=message['threadId'],
                        body=unicode(body, 'utf-8'),
                        email_to=meta.get('to', ''),
                        email_from=meta.get('from', ''),
                        subject=meta.get('subject', ''),
                        time=date
                    )

        except errors.HttpError as e:
            print(e)

def extract_messages(extractor, messages):
    """
    Extract the given messages into the db.

    Args:
        extractor: object - the extractor to use to extract the messages
        messages: list - a list of messages to store in the db
    """
    session = models.db_session()
    ids = [message['id'] for message in messages]
    existing = session.query(models.Email.external_id) \
                .filter(models.Email.external_id.in_(ids)) \
                .all()
    existing_ids = [item[0] for item in existing] 

    for message in messages:
        # if we already have this message in the db
        # we don't need to recreate it
        if message['id'] in existing_ids:
            continue

        email = extractor.generate_email(
                    message['id'], message['threadId'])

        if not email:
            continue

        session.add(email)

    # commit the records
    session.commit()

def run():
    """
    Run extraction.
    """
    extractor = GMailExtractor(api_service())
    messages = extractor.messages(query=config.gmail_query)
    print('Extracting first page.')
    extract_messages(extractor, messages)

    while extractor.page_token():
        print('Extracting page {}.'.format(extractor.page_token()))
        messages = extractor.messages(query=config.gmail_query)
        extract_messages(extractor, messages)

if __name__ == '__main__':
    run()
