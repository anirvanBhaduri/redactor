"""
The redact module.
"""

import config
import models
import sys
import re
import traceback
from HTMLParser import HTMLParser

def match_phone_numbers(content):
    """
    Given a string input, find all phone numbers in that
    string.

    Input:
    content - string - the content to look through

    Returns:
    list - a list of matches
    """
    if not isinstance(content, basestring):
        raise ValueError('content must be a string.')

    patterns = [
        "\\(?\\d{3}\\)?[.-]? *\\d{3}[.-]? *[.-]?\\d{4}",
        "\\(\\d{3}\\)\\s\\d{3}-\\d{4}",
        "\(\d{2,4}\)\d{6,7}",
        "\(\d{2,4}\) \d{6,7}"
    ]

    matches = []

    for pattern in patterns:
        matches.extend(re.findall(pattern, content))

    return matches

def redact_phone_numbers(content):
    """
    Redact any phone numbers from some given content.
    """
    for number in match_phone_numbers(content):
        content = content.replace(number, config.redaction_string)

    return content

def match_email_address(content):
    """
    Given a string input, find all email addresses in that
    string.

    Input:
    content - string - the content to look through

    Returns:
    list - a list of matches
    """
    if not isinstance(content, basestring):
        raise ValueError('content must be a string.')

    pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    return re.findall(pattern, content)

def redact_email_address(content):
    """
    Redact any email addresses from some given content.

    This method makes use of the configuration 'excludes' to 
    exclude the redaction of some email addresses.
    """
    def replace(match, content):
        """
        Exclude the replacement of any 'excludes'.
        """
        for exclusion in config.excludes:
            if exclusion in match:
                return content

        return content.replace(match, config.redaction_string)

    for match in match_email_address(content):
        content = replace(match, content)

    return content

def match_ip_address(content):
    """
    Given a string input, find all ip addresses in that string.

    Input:
    content - string - the content to look through

    Returns:
    list - a list of matches
    """
    if not isinstance(content, basestring):
        raise ValueError('content must be a string.')

    pattern = "\b((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.|$)){4}\b"
    return re.findall(pattern, content)

def redact_ip_address(content):
    """
    Redact any ip addresses from some given content.
    """
    for match in match_ip_address(content):
        content = content.replace(match, config.redaction_string)

    return content

class EmailHtmlParser(HTMLParser):
    """
    An email Html Parser.

    This parses html content from emails containing
    delivery addresses and other sensitive information.
    """

    def __init__(self):
        """
        EmailHtmlParser constructor.
        """
        self.redacting = False
        self.reset()
        self.newtags = []
        self.newattrs = []
        self.htmldata = []
        self.trs = []

    def handle_starttag(self, tag, attrs):
        """
        Handler to run when a start tag is encountered.

        Takes note of how many trs, tags and attrs are 
        encountered, to ensure it can correctly deconstruct
        the html.
        """
        self.newtags.append(tag)
        self.newattrs.append(attrs)

        hrefs = [item for item in attrs if 'href' in item]

        if hrefs and '?member=' in hrefs[0][1]:
            self.redacting = True

        if 'tr' in tag:
            self.trs.append(len(self.htmldata))

        if self.redacting:
            self.htmldata.append('<' + tag + '>')
            return

        if tag is not 'html':
            self.htmldata.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        """
        Handler to run when an end tag is encountered.

        Takes not of how many trs, tags and attrs
        are encountered, to ensure it can correctly construct
        the html again.
        """
        if 'tr' in tag:
            self.trs.append(len(self.htmldata))

        if self.redacting:
            self.redacting = False

        if tag is not 'html':
            self.htmldata.append('</' + tag + '>')

        if len(self.trs) == 2:
            check = ''.join(self.htmldata[self.trs[0]:self.trs[1]])
            if 'Delivery address' in check:
                one = self.htmldata[0:self.trs[0]-1]
                two = self.htmldata[self.trs[1]:]
                final = one + two
                self.htmldata = final
            self.trs = []

    def handle_data(self, data):
        """
        Add the redaction string to the html data.
        """
        if self.redacting:
            self.htmldata.append(config.redaction_string)
            return

        self.htmldata.append(data)

    def clean(self):
        """
        Empty out the html tag counters.
        """
        self.newtags = []
        self.newattrs = []
        self.htmldata = []

    def parsed_data(self):
        """
        Get redacted and constructed html data as a string.

        Returns:
        string - the redacted html string.
        """
        return ''.join(self.htmldata)

def redact_email(email):
    """
    Given an Email, redact the Email of redactable contents and
    generate a RedactedEmail.

    Input:
    email - Email - the email to be redacted.

    Returns:
    RedactedEmail - the redacted email instance.
    """
    subject = email.subject
    email_from = email.email_from
    email_to = email.email_to
    body = email.body

    redacted_subject = redact_email_address(subject)
    redacted_subject = redact_ip_address(redacted_subject)
    redacted_subject = redact_phone_numbers(redacted_subject)

    redacted_email_from = redact_email_address(email_from)
    redacted_email_to = redact_email_address(email_to)

    # we need to parse the html content for the body as well
    parser = EmailHtmlParser()
    parser.feed(body)

    redacted_body = parser.parsed_data()
    redacted_body = redact_email_address(redacted_body)
    redacted_body = redact_ip_address(redacted_body)
    redacted_body = redact_phone_numbers(redacted_body)

    return models.RedactedEmail(
                id=email.id,
                subject=redacted_subject,
                email_from=redacted_email_from,
                email_to=redacted_email_to,
                time=email.time,
                body=redacted_body)

def run():
    """
    Run redaction.
    """
    session = models.db_session()

    try:
        # go through each email and redact it
        for email in session.query(models.Email).all():
            session.add(redact_email(email))

        session.commit()

    # rollback if any failures
    except Exception as e:
        session.rollback()

        # print the exception
        ex_type, ex, tb = sys.exc_info()
        traceback.print_tb(tb)
        print(e.message)

if __name__ == '__main__':
    run()
