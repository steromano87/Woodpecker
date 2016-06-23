import sqlite3
import pkg_resources


class DBWriter(object):

    def __init__(self, str_file_path):
        # Connection handler
        self._conn = sqlite3.connect(str_file_path)

        # Cursor
        self.cursor = self._conn.cursor()

        # DB creation script
        self._db_creation_script = \
            pkg_resources.resource_string('woodpecker.logging',
                                          'db_creation.sql')

        # Initialize DB
        self._initialize_db()

    def _initialize_db(self):
        self.cursor.executescript(self._db_creation_script)

    def insert_in_section(self, str_section, lst_data):
        self.cursor.execute('BEGIN TRANSACTION')
        for dic_data in lst_data:
            self._insert_entry_in_section(str_section, dic_data)
        self.cursor.execute('COMMIT')

    def _insert_entry_in_section(self, str_section, dic_data):
        str_insert_string = \
            'INSERT INTO {table} ({columns}) values ({values})'.format(
                table=str_section,
                columns=', '.join(dic_data.keys()),
                values=', '.join(['?' for _ in dic_data.itervalues()])
            )
        self.cursor.execute(str_insert_string, dic_data.itervalues())
