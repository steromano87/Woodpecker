import sqlite3

__author__ = 'Stefano.Romano'


class DBWriter(object):

    def __enter__(self, str_filepath):

        # Create the DB
        self.conn = sqlite3.connect(str_filepath)
        self.cursor = self.conn.cursor()

        # Creates the tables
        # Transactions table
        str_transactions_table_query = 'CREATE TABLE IF NOT EXISTS transactions (' \
                                       'hostName TEXT DEFAULT \'LOCALHOST\',' \
                                       'spawnID TEXT,' \
                                       'testName TEXT,' \
                                       'iteration INTEGER,' \
                                       'transactionName TEXT,' \
                                       'startTimestamp TEXT,' \
                                       'endTimestamp TEXT' \
                                       ');'
        str_transactions_index_query = 'CREATE INDEX IF NOT EXISTS transactions_mainkeys ' \
                                       'on transactions (hostName, spawnID, testName, iteration, transactionName);'

        # Requests table
        str_requests_table_query = 'CREATE TABLE IF NOT EXISTS requests (' \
                                   'hostName TEXT DEFAULT \'LOCALHOST\',' \
                                   'spawnID TEXT,' \
                                   'testName TEXT,' \
                                   'iteration INTEGER,' \
                                   'timeStamp TEXT,' \
                                   'requestName TEXT,' \
                                   'requestType TEXT,' \
                                   'requestSkeleton TEXT,' \
                                   'requestSpecs BLOB,' \
                                   'duration INTEGER,' \
                                   'status TEXT,' \
                                   'responseSize INTEGER,' \
                                   'assertionResult INTEGER DEFAULT 1);'
        str_requests_main_index_query = 'CREATE INDEX IF NOT EXISTS requests_mainkeys ' \
                                        'on requests (hostName, spawnID, testName, iteration, requestName);'
        str_requests_timestamp_index_query = 'CREATE INDEX IF NOT EXISTS requests_timestamp ' \
                                             'on requests (timeStamp);'
        str_requests_status_code_index_query = 'CREATE INDEX IF NOT EXISTS requests_statuscode ' \
                                               'on requests (statusCode);'
        str_requests_skeleton_index_query = 'CREATE INDEX IF NOT EXISTS requests_skeleton ' \
                                            'on requests (requestSkeleton);'
        str_requests_assertion_index_query = 'CREATE INDEX IF NOT EXISTS requests_assertions ' \
                                             'on requests (assertionResult);'

        # Running spawns table
        str_spawns_table_query = 'CREATE TABLE IF NOT EXISTS spawns (' \
                                 'hostName TEXT DEFAULT \'LOCALHOST\',' \
                                 'timeStamp TEXT,' \
                                 'plannedSpawns INTEGER,' \
                                 'runningSpawns INTEGER' \
                                 ');'
        str_spawns_main_index_query = 'CREATE INDEX IF NOT EXISTS spawns_mainkeys ' \
                                      'as spawns (hostName, timeStamp);'

        # System monitor table
        str_sysmonitor_table_query = 'CREATE TABLE IF NOT EXISTS sysmonitor (' \
                                     'hostName TEXT DEFAULT \'LOCALHOST\',' \
                                     'timeStamp TEXT,' \
                                     'CPU_perc REAL,' \
                                     'memory_used INTEGER,' \
                                     'memory_avail INTEGER,' \
                                     'memory_perc REAL,' \
                                     'bytes_sent INTEGER,' \
                                     'bytes_recv INTEGER' \
                                     ');'
        str_sysmonitor_main_index_query = 'CREATE INDEX IF NOT EXISTS sysmonitor_mainkeys ' \
                                          'as sysmonitor (hostName, timeStamp);'

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
            str_sysmonitor_table_query,
            str_sysmonitor_main_index_query
        )))

        self.conn.commit()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()

    def write_transaction_start(self,
                          str_hostname,
                          str_spawn_id,
                          str_test_name,
                          str_iteration,
                          str_transaction_name,
                          str_start_timestamp):
        str_prepared = 'INSERT INTO transactions ' \
                       'values (?, ?, ?, ?, ?, ?, NULL)'
        self.cursor.execute(str_prepared,
                            (
                                str_hostname,
                                str_spawn_id,
                                str_test_name,
                                str_iteration,
                                str_transaction_name,
                                str_start_timestamp
                            )
                            )
        self.conn.commit()
