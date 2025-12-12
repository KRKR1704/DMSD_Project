import sqlite3
import os

BASE = os.path.dirname(__file__)
SQL_DIR = os.path.join(BASE, 'sql')
DB_PATH = os.path.join(BASE, 'labmanager.db')

def run_sql_file(conn, path):
    with open(path, 'r', encoding='utf8') as f:
        sql = f.read()
    conn.executescript(sql)

if __name__ == '__main__':
    if os.path.exists(DB_PATH):
        print('Removing old DB at', DB_PATH)
        os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    run_sql_file(conn, os.path.join(SQL_DIR, 'schema_sqlite.sql'))
    run_sql_file(conn, os.path.join(SQL_DIR, 'sample_data.sql'))
    conn.commit()
    conn.close()
    print('Initialized database at', DB_PATH)
