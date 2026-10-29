-- Viraloop: single-account state store.
CREATE TABLE IF NOT EXISTS kv (
  key   TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS activity (
  id     INTEGER PRIMARY KEY AUTOINCREMENT,
  ts     INTEGER NOT NULL,
  type   TEXT NOT NULL,
  title  TEXT NOT NULL,
  detail TEXT
);

CREATE INDEX IF NOT EXISTS idx_activity_ts ON activity (ts DESC);
