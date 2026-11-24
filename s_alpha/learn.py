import sqlite3

def record(db, task_id):
    with sqlite3.connect(db) as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS evaluations (task_id TEXT PRIMARY KEY)')
        conn.execute('INSERT INTO evaluations VALUES (?)', (task_id,))

def score(db):
    with sqlite3.connect(db) as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS evaluations (task_id TEXT PRIMARY KEY)')
        return conn.execute('SELECT COUNT(*) FROM evaluations').fetchone()[0]
