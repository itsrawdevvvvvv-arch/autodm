"""Validate every SQL statement in worker.js against a real SQLite engine."""
import re
import sqlite3
import sys

SRC = "/scratch/work/autodm/worker.js"
MIG = "/scratch/work/autodm/migrations/0001_init.sql"

src = open(SRC, encoding="utf-8").read()

# SQL strings passed to env.DB.prepare(...) — single or double quoted, may be concatenated
statements = []
for m in re.finditer(r"\.prepare\(\s*(['\"])(.*?)\1", src, re.S):
    statements.append(m.group(2))
for m in re.finditer(r"\.prepare\(\s*'([^']*)'\s*\+\s*([^)]+)\)", src, re.S):
    pass

db = sqlite3.connect(":memory:")
db.executescript(open(MIG, encoding="utf-8").read())
print(f"migration applied: {len(statements)} statements found in worker.js")

fails = 0
for sql in statements:
    flat = re.sub(r"\s+", " ", sql).strip()
    params = flat.count("?")
    try:
        db.execute("EXPLAIN " + flat, [None] * params)
    except Exception as e:
        fails += 1
        print(f"  ✗ {flat[:90]}…\n     {e}")

print(f"sql errors: {fails}")

# Round-trip the upsert and the trim query for real.
db.execute("INSERT INTO kv (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value", ("rules", "[]"))
db.execute("INSERT INTO kv (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value", ("rules", "[1]"))
assert db.execute("SELECT value FROM kv WHERE key = ?", ("rules",)).fetchone()[0] == "[1]", "upsert failed"
for i in range(305):
    db.execute("INSERT INTO activity (ts, type, title, detail) VALUES (?, ?, ?, ?)", (i, "message", "t", "d"))
db.execute("DELETE FROM activity WHERE id NOT IN (SELECT id FROM activity ORDER BY id DESC LIMIT 300)")
rows = db.execute("SELECT COUNT(*) FROM activity").fetchone()[0]
print(f"upsert ok · activity trim keeps {rows} rows (expected 300)")
assert rows == 300, "trim failed"
n = db.execute("SELECT COUNT(*) AS n FROM activity WHERE type = ? AND ts > ?", ("message", 10)).fetchone()[0]
print(f"hourly count query ok ({n})")
sys.exit(1 if fails else 0)
