"""
The transform module.

Convert stored data to a user friendly
table.

Author: Anirvan Bhaduri
Since: 10th Nov 2018
"""

from html import HTML

import models
import config
import os

def create_table(headers, rows):
    """
    Create and return an HTML table object given
    a list of rows.

    Args:
        headers: list containing table headers
        rows: list of lists containing the rows of the table

        headers and rows must be the same length

    Returns:
        table: the table containing the input rows
    """
    if not isinstance(headers, TableHeader):
        raise ValueError('Must provide TableHeader.')
    
    if not len(rows) or not isinstance(rows[0], TableRow):
        raise ValueError('Must provide TableRow.')

    h = HTML()
    table = h.table(border='1')
    body = table.tbody
    body.text(headers.html_element(), escape=False)

    for row in rows:
        body.text(row.html_element(), escape=False)

    return table

class TableRow(object):
    """
    Class to capture an html table row.
    """

    def __init__(self, row, link):
        """
        TableRow constructor.

        Args:
            row: A list containing tuples of the form ("header", "value").
            link: The link to the file on the row
        """
        if not isinstance(row, list):
            raise ValueError('The row must be a python list.')

        self._row = row
        self._link = link
        self._html = HTML()

    def html_element(self):
        """
        Return the HTML element representing the 
        table row.
        """
        row = self._html.tr
        
        for header, item in self._row:
            row.td(item, escape=False)

        row.td.a(self._link, href=self._link, escape=False)
        return row

class TableHeader(TableRow):
    """
    TableHeader class to capture the table header.
    """

    def html_element(self):
        """
        Return the HTML element representing the table
        headers.
        """
        row = self._html.tr

        for header, item in self._row:
            row.th.b(header)

        row.th.b('Link')
        return row

class Row(object):
    """
    Row that converts emails to table compatible
    rows.
    """
    def __init__(self, email, template):
        """
        Row constructor.

        Args:
            email: an email object
            template: list - list of tuples, 
                                the template to use to convert row
        """
        self._email = email
        email_dict = email.__dict__
        self._row = []

        for key, value in template:
            self._row.append((value, email_dict.get(key)))

    def get(self):
        """
        Get the converted row.

        Returns:
            list: the converted row
        """
        return self._row

    def link_file(self, root):
        """
        Generate a file in the given root.

        Then update the row to contain a relative link from
        the root specified.

        Args:
            root: the root folder where a file will be generated
        """
        directory = 'files'

        if not os.path.exists('{}/{}'.format(root, directory)):
            os.makedirs('{}/{}'.format(root, directory))

        email_type = self._email.__tablename__
        filename = 'file.id.{}.{}'.format(self._email.id, email_type)
        path_to_file = "{}/{}/{}". \
                        format(root, directory, filename)

        with open(path_to_file, 'w') as f:
            f.write(self._email.body.encode('utf8'))

        return '{}/{}'.format(directory, filename)

def commit_table(table, name, root):
    """
    Create a file with the current table at the root.
    """
    if not os.path.exists(root):
        os.makedirs(root)

    with open('{}/{}'.format(root, name), 'w') as f:
        f.write(unicode(table).encode('utf8'))

def run():
    """
    Run transformation.
    """
    session = models.db_session()

    base_id = 0

    # use config for query
    while True:
        emails = session.query(
            models.__dict__[config.email_type]) \
                .filter(models.__dict__[config.email_type].id>base_id) \
                    .limit(1000).all()

        # discontinue if no more emails to go through
        if not len(emails):
            break

        rows = [Row(email, config.table_columns) for email in emails]
        table_header = TableHeader(rows[0].get(), '')

        table_rows = [
            TableRow(row.get(), row.link_file(config.generation_root)) 
                                                        for row in rows
        ]
    
        table = create_table(table_header, table_rows)
        commit_table(
                table, '{}--{}.index.html'.format(base_id+1, emails[-1].id), 
                config.generation_root)

        base_id = emails[-1].id

if __name__ == '__main__':
    run()
