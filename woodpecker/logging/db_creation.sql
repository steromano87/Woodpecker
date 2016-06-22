-- Create results database

-- Transactions table
CREATE TABLE IF NOT EXISTS transactions (
  hostName TEXT DEFAULT 'localhost',
  peckerID TEXT,
  navigationName TEXT,
  transactionName TEXT,
  iteration INTEGER,
  startTimestamp TEXT,
  endTimestamp TEXT
);
CREATE INDEX IF NOT EXISTS transactions_mainkeys
on transactions (
  hostName,
  peckerID,
  navigationName,
  transactionName,
  iteration
);


-- Steps table
CREATE TABLE IF NOT EXISTS steps (
  hostName TEXT DEFAULT 'localhost',
  peckerID TEXT,
  navigationName TEXT,
  transactionName TEXT,
  stepName TEXT,
  stepType  TEXT,
  iteration INTEGER,
  timestamp TEXT,
  stepSkeleton BLOB,
  stepData BLOB,
  elapsed INTEGER,
  status TEXT,
  responseSize INTEGER,
  assertionsResult INTEGER DEFAULT NULL
);
CREATE INDEX IF NOT EXISTS requests_mainkeys
on steps (hostName, peckerID, navigationName, stepName, iteration);
CREATE INDEX IF NOT EXISTS requests_timestamp
on steps (timestamp);
CREATE INDEX IF NOT EXISTS requests_status
on steps (status);
CREATE INDEX IF NOT EXISTS requests_skeleton
on steps (stepSkeleton);
CREATE INDEX IF NOT EXISTS requests_assertions
on steps (assertionsResult);


-- Peckers table
-- TODO: add table definition


-- Sysmonitor table
CREATE TABLE IF NOT EXISTS sysmonitor (
hostName TEXT DEFAULT 'localhost',
timestamp TEXT,
hostType TEXT DEFAULT 'spawner',
CPUperc REAL,
memoryUsed INTEGER,
memoryAvail INTEGER,
memoryPerc REAL
);
CREATE INDEX IF NOT EXISTS sysmonitor_mainkeys
on sysmonitor (hostName, timestamp);
CREATE INDEX IF NOT EXISTS sysmonitor_hostType
on sysmonitor (hostType);


-- Events table
-- TODO: add events table


-- SLA table
-- TODO: add SLA table
