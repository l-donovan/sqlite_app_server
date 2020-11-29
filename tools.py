import sqlite3

def db_create(filename, name='admin'):
    conn = sqlite3.connect(filename)
    curs = conn.cursor()

    curs.execute('CREATE TABLE meta (key text PRIMARY KEY, value text)')
    curs.execute('CREATE TABLE html (filename text PRIMARY KEY, data blob)')

    pairs = [
        ('app_file_name', filename),
        ('app_file_author', name),
        ('app_file_entry_point', '/html/index.html'),
        ('app_file_404_page', '/html/404.html')
    ]

    curs.executemany('INSERT INTO meta VALUES (?, ?)', pairs)

    files = [
        ('index.html', b'<html><body><h1>Hello, World! <a href="/html/test.html">Click here</a></h1></body></html>'),
        ('404.html', b'<html><head><title>404</title></head><body><h1>This is a custom 404 page</h1></body></html>'),
        ('test.html', b'<html><body><h1>This is a test</h1></body></html>')
    ]

    curs.executemany('INSERT INTO html VALUES (?, ?)', files)

    conn.commit()
    conn.close()

def db_verify(filename):
    conn = sqlite3.connect(filename)
    curs = conn.cursor()

    curs.execute('pragma table_info("meta")')
    print(curs.fetchall())

    curs.execute('pragma table_info("html")')
    print(curs.fetchall())

    conn.commit()
    conn.close()