import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from .config import DATA

def now():
    return datetime.now(timezone.utc).isoformat()

@contextmanager
def db():
    con = sqlite3.connect(DATA / 'studio.db', timeout=30)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    finally:
        con.close()

def init():
    with db() as c:
        c.executescript('''
        PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS jobs (
          id TEXT PRIMARY KEY, topic TEXT, spec TEXT, mode TEXT, status TEXT,
          research TEXT, script TEXT, artifacts TEXT, error TEXT, created_at TEXT,
          approved INTEGER DEFAULT 0, feedback TEXT);
        CREATE TABLE IF NOT EXISTS events (
          id INTEGER PRIMARY KEY, job_id TEXT, stage TEXT, message TEXT, created_at TEXT);
        CREATE TABLE IF NOT EXISTS sources (
          id INTEGER PRIMARY KEY, payload TEXT, created_at TEXT);
        CREATE TABLE IF NOT EXISTS observations (
          url TEXT, views INTEGER, observed_at TEXT);
        CREATE TABLE IF NOT EXISTS publications (
          id INTEGER PRIMARY KEY, job_id TEXT, platform TEXT, status TEXT,
          scheduled_at TEXT, privacy TEXT, result TEXT, created_at TEXT,
          UNIQUE(job_id, platform));
        CREATE TABLE IF NOT EXISTS skills (name TEXT PRIMARY KEY, body TEXT);
        ''')
        columns = {r['name'] for r in c.execute('PRAGMA table_info(publications)')}
        if 'provider' not in columns:
            # Old queued TikTok entries remain manual, even if .env is changed later.
            c.execute("ALTER TABLE publications ADD COLUMN provider TEXT NOT NULL DEFAULT 'native'")
        # Recover interrupted local work; never blindly repeat an external upload.
        c.execute("UPDATE jobs SET status='failed', error='Generation was interrupted. You can retry.' WHERE status IN ('queued','researching','writing','producing')")
        c.execute("UPDATE publications SET status='unknown', result=? WHERE status='sending'", (json.dumps({'message': 'Upload was interrupted. Check YouTube Studio before creating another post.'}),))

def event(job_id, stage, message):
    with db() as c:
        c.execute('INSERT INTO events(job_id,stage,message,created_at) VALUES(?,?,?,?)', (job_id, stage, message, now()))

def update(job_id, **fields):
    allowed = {'status', 'research', 'script', 'artifacts', 'error', 'approved', 'feedback'}
    if not fields or not set(fields) <= allowed:
        raise ValueError('Invalid job fields')
    vals = [json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v for v in fields.values()]
    with db() as c:
        c.execute('UPDATE jobs SET ' + ','.join(f'{k}=?' for k in fields) + ' WHERE id=?', (*vals, job_id))

def decode(row):
    item = dict(row)
    for k in ('spec', 'research', 'script', 'artifacts', 'feedback', 'result'):
        if k in item and item[k]:
            item[k] = json.loads(item[k])
    return item

def job(job_id):
    with db() as c:
        row = c.execute('SELECT * FROM jobs WHERE id=?', (job_id,)).fetchone()
        if not row:
            return None
        result = decode(row)
        result['events'] = [dict(r) for r in c.execute('SELECT * FROM events WHERE job_id=? ORDER BY id', (job_id,))]
        result['publications'] = [decode(r) for r in c.execute('SELECT * FROM publications WHERE job_id=? ORDER BY id', (job_id,))]
        return result
