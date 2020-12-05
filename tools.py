import sqlite3


def sanitize(sql):
    return ''.join(c for c in sql if c.isalnum())


def db_verify(filename):
    conn = sqlite3.connect(filename)
    curs = conn.cursor()

    curs.execute('pragma table_info("meta")')
    print(curs.fetchall())

    curs.execute('pragma table_info("html")')
    print(curs.fetchall())

    conn.commit()
    conn.close()

