import sqlite3

def get_db():
    conn = sqlite3.connect('legal.db')  # Wahi purana database
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_number TEXT,
            title TEXT,
            client_name TEXT,
            case_type TEXT,
            status TEXT,
            date_filed TEXT
        )
    ''')
    conn.commit()
    conn.close()