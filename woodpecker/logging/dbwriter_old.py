import sqlite3

__author__ = 'Stefano.Romano'


class DBWriter(object):

    def __init__(self, str_filepath):
        self.__create_database(str_filepath)

    def __enter__(self, str_filepath):
        self.__create_database(str_filepath)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__disconnect()

    def __del__(self):
        self.__disconnect()

    def __disconnect(self):
        self.conn.commit()
        self.conn.close()

    def __create_database(self, str_filepath):
        # Create the DB
        self.conn = sqlite3.connect(str_filepath)
        self.cursor = self.conn.cursor()

        # Creates the tables
        # Transactions table
        str_transactions_table_query = 'CREATE TABLE IF NOT EXISTS transactions (' \
                                       'hostName TEXT DEFAULT \'LOCALHOST\',' \
                                       'peckerID TEXT,' \
                                       'navigationName TEXT,' \
                                       'iteration INTEGER,' \
                                       'transactionName TEXT,' \
                                       'startTimestamp TEXT,' \
                                       'endTimestamp TEXT' \
                                       ');'
        str_transactions_index_query = 'CREATE INDEX IF NOT EXISTS transactions_mainkeys ' \
                                       'on transactions (hostName, peckerID, navigationName, iteration, transactionName);'

        # Requests table
        str_requests_table_query = 'CREATE TABLE IF NOT EXISTS requests (' \
                                   'hostName TEXT DEFAULT \'LOCALHOST\',' \
                                   'peckerID TEXT,' \
                                   'navigationName TEXT,' \
                                   'iteration INTEGER,' \
                                   'timestamp TEXT,' \
                                   'requestName TEXT,' \
                                   'requestType TEXT,' \
                                   'requestSkeleton TEXT,' \
                                   'requestSpecs BLOB,' \
                                   'duration INTEGER,' \
                                   'status TEXT,' \
                                   'responseSize INTEGER,' \
                                   'assertionResult INTEGER DEFAULT 1);'
        str_requests_main_index_query = 'CREATE INDEX IF NOT EXISTS requests_mainkeys ' \
                                        'on requests (hostName, peckerID, navigationName, iteration, requestName);'
        str_requests_timestamp_index_query = 'CREATE INDEX IF NOT EXISTS requests_timestamp ' \
                                             'on requests (timestamp);'
        str_requests_status_code_index_query = 'CREATE INDEX IF NOT EXISTS requests_status ' \
                                               'on requests (status);'
        str_requests_skeleton_index_query = 'CREATE INDEX IF NOT EXISTS requests_skeleton ' \
                                            'on requests (requestSkeleton);'
        str_requests_assertion_index_query = 'CREATE INDEX IF NOT EXISTS requests_assertions ' \
                                             'on requests (assertionResult);'

        # Running spawns table
        str_spawns_table_query = 'CREATE TABLE IF NOT EXISTS spawns (' \
                                 'hostName TEXT DEFAULT \'LOCALHOST\',' \
                                 'timestamp TEXT,' \
                                 'navigationName TEXT,' \
                                 'plannedSpawns INTEGER,' \
                                 'runningSpawns INTEGER' \
                                 ');'
        str_spawns_main_index_query = 'CREATE INDEX IF NOT EXISTS spawns_mainkeys ' \
                                      'on spawns (hostName, timestamp);'

        # System monitor table
        str_sysmonitor_table_query = 'CREATE TABLE IF NOT EXISTS sysmonitor (' \
                                     'hostName TEXT DEFAULT \'LOCALHOST\',' \
                                     'timestamp TEXT,' \
                                     'hostType TEXT DEFAULT \'SPAWNER\',' \
                                     'CPUperc REAL,' \
                                     'memoryUsed INTEGER,' \
                                     'memoryAvail INTEGER,' \
                                     'memoryPerc REAL' \
                                     ');'
        str_sysmonitor_main_index_query = 'CREATE INDEX IF NOT EXISTS sysmonitor_mainkeys ' \
                                          'on sysmonitor (hostName, timestamp);'
        str_sysmonitor_host_type_index_query = 'CREATE INDEX IF NOT EXISTS sysmonitor_hostType ' \
                                               'on sysmonitor (hostType);'

        # Messages table
        str_messages_table_query = 'CREATE TABLE IF NOT EXISTS messages (' \
                                   'hostName TEXT DEFAULT \'LOCALHOST\',' \
                                   'peckerID TEXT, ' \
                                   'navigationName TEXT, ' \
                                   'iteration INTEGER, ' \
                                   'timestamp TEXT, ' \
                                   'message BLOB' \
                                   ');'
        str_messages_main_index_query = 'CREATE INDEX IF NOT EXISTS messages_mainkeys ' \
                                        'on messages (hostName, peckerID, navigationName, iteration);'
        str_messages_timestamp_index_query = 'CREATE INDEX IF NOT EXISTS messages_timestamp ' \
                                             'on messages (timestamp);'

        # Executes all the queries as script
        self.cursor.executescript('\n'.join((
            str_transactions_table_query,
            str_transactions_index_query,
            '\n',
            str_requests_table_query,
            str_requests_main_index_query,
            str_requests_timestamp_index_query,
            str_requests_status_code_index_query,
            str_requests_skeleton_index_query,
            str_requests_assertion_index_query,
            '\n',
            str_spawns_table_query,
            str_spawns_main_index_query,
            '\n',
            str_sysmonitor_table_query,
            str_sysmonitor_main_index_query,
            str_sysmonitor_host_type_index_query,
            '\n',
            str_messages_table_query,
            str_messages_main_index_query,
            str_messages_timestamp_index_query
        )))

        self.conn.commit()

    def write_transaction_start(self, dic_payload):
        str_prepared = 'INSERT INTO transactions ' \
                       'VALUES (?, ?, ?, ?, ?, ?, NULL)'
        self.cursor.execute(str_prepared,
                            (
                                dic_payload.get('hostName'),
                                dic_payload.get('peckerID'),
                                dic_payload.get('navigationName'),
                                dic_payload.get('iteration'),
                                dic_payload.get('transactionName'),
                                dic_payload.get('startTimestamp')
                            )
                            )
        self.conn.commit()

    def write_transaction_end(self, dic_payload):
        str_prepared = 'UPDATE transactions ' \
                       'SET endTimestamp = ? ' \
                       'WHERE hostName = ? ' \
                       '    AND peckerID = ? ' \
                       '    AND navigationName = ? ' \
                       '    AND iteration = ? ' \
                       '    AND transactionName = ?'
        self.cursor.execute(str_prepared,
                            (
                                dic_payload.get('endTimestamp'),
                                dic_payload.get('hostName'),
                                dic_payload.get('peckerID'),
                                dic_payload.get('navigationName'),
                                dic_payload.get('iteration'),
                                dic_payload.get('transactionName')
                            )
                            )
        self.conn.commit()

    def write_request(self, dic_payload):
        str_prepared = 'INSERT INTO requests ' \
                       'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        self.cursor.execute(str_prepared,
                            (
                                dic_payload.get('hostName'),
                                dic_payload.get('peckerID'),
                                dic_payload.get('navigationName'),
                                dic_payload.get('iteration'),
                                dic_payload.get('timestamp'),
                                dic_payload.get('requestName'),
                                dic_payload.get('requestType'),
                                dic_payload.get('requestSkeleton'),
                                dic_payload.get('requestSpecs'),
                                dic_payload.get('duration'),
                                dic_payload.get('status'),
                                dic_payload.get('responseSize'),
                                dic_payload.get('assertionResult')
                            )
                            )
        self.conn.commit()

    def write_spawns_info(self, dic_payload):
        str_prepared = 'INSERT INTO spawns ' \
                       'VALUES (?, ?, ?, ?, ?)'
        self.cursor.execute(str_prepared,
                            (
                                dic_payload.get('hostName'),
                                dic_payload.get('timestamp'),
                                dic_payload.get('navigationName'),
                                dic_payload.get('plannedSpawns'),
                                dic_payload.get('runningSpawns')
                            )
                            )
        self.conn.commit()

    def write_sysmonitor_info(self, dic_payload):
        str_prepared = 'INSERT INTO sysmonitor ' \
                       'VALUES (?, ?, ?, ?, ?, ?, ?)'
        self.cursor.execute(str_prepared,
                            (
                                dic_payload.get('hostName'),
                                dic_payload.get('timestamp'),
                                dic_payload.get('hostType'),
                                dic_payload.get('CPUperc'),
                                dic_payload.get('memoryUsed'),
                                dic_payload.get('memoryAvail'),
                                dic_payload.get('memoryPerc')
                            )
                            )
        self.conn.commit()

    def write_message(self, dic_payload):
        str_prepared = 'INSERT INTO messages ' \
                       'VALUES (?, ?, ?, ?, ?, ?)'
        self.cursor.execute(str_prepared,
                            (
                                dic_payload.get('hostName'),
                                dic_payload.get('peckerID'),
                                dic_payload.get('navigationName'),
                                dic_payload.get('iteration'),
                                dic_payload.get('timestamp'),
                                dic_payload.get('messages')
                            )
                            )
        self.conn.commit()