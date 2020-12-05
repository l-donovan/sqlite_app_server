from os import path
from tools import sanitize
import http.server
import re
import socketserver
import sqlite3


class AppFile:
    def __init__(self, file_path, author='admin'):
        self.file_path = file_path
        self.file_name = path.splitext(path.basename(self.file_path))[0]
        self.author = author
        self.conn = None
        self.curs = None

    def __enter__(self):
        is_new_file = not path.exists(self.file_path)

        self.conn = sqlite3.connect(self.file_path)
        self.curs = self.conn.cursor()

        if is_new_file:
            self.create()

        return self

    def __exit__(self, exc_type, exc_value, exc_trace):
        self.curs.close()
        self.conn.close()

        return True

    def __repr__(self):
        return f'AppFile<{self.file_name}>'

    def create(self):
        self.curs.execute('CREATE TABLE meta (key text PRIMARY KEY, value text)')
        self.curs.execute('CREATE TABLE html (filename text PRIMARY KEY, data blob)')
        self.curs.execute('CREATE TABLE image (filename text PRIMARY KEY, data blob)')

        pairs = [
            ('app_file_name', self.file_name),
            ('app_file_author', self.author),
            ('app_file_entry_point', '/html/index.html'),
            ('app_file_404_page', '/html/404.html'),
            ('app_file_favicon', '/image/favicon.ico')
        ]

        self.curs.executemany('INSERT INTO meta VALUES (?, ?)', pairs)

        files = [
            ('index.html', b'<html><body><h1>Hello, World!<br><a href="/html/test.html">Click here</a></h1></body></html>'),
            ('404.html', b'<html><head><title>404</title></head><body><h1>This is a custom 404 page</h1></body></html>'),
            ('test.html', b'<html><body><h1>This is a test</h1></body></html>')
        ]

        self.curs.executemany('INSERT INTO html VALUES (?, ?)', files)

        self.conn.commit()

    def meta_get(self, key):
        self.curs.execute('SELECT value FROM meta WHERE key=?', (key,))
        if data := self.curs.fetchone():
            return data[0]

        return False

    def file_add(self, table, filename, file_bytes):
        if self.curs and self.conn:
            self.curs.execute(f'REPLACE INTO {sanitize(table)} VALUES (?, ?)', (filename, file_bytes))
            self.conn.commit()

    def file_remove(self, table, filename):
        if self.curs and self.conn:
            self.curs.execute(f'DELETE FROM {sanitize(table)} WHERE filename=?', (filename,))
            self.conn.commit()

    def file_get(self, table, filename):
        if self.curs and self.conn:
            self.curs.execute(f'SELECT data FROM {sanitize(table)} WHERE filename=?', (filename,))
            if data := self.curs.fetchone():
                return data[0]

        return False


class FileRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        data = self.server.retrieve(self.path)
        self.wfile.write(data)


class AppFileServer(socketserver.TCPServer):
    def __init__(self, app_file, port=8123, *args, **kwargs):
        self.app_file = app_file
        self.conn = None
        self.curs = None
        self.port = port
        super().__init__(('', self.port), FileRequestHandler)

    def file_from_path(self, path):
        if match := re.match(r'/(\w+)/([\w\.]+)', path):
            table = sanitize(match.group(1))
            filename = match.group(2)

            if (data := self.app_file.file_get(table, filename)) != False:
                return data

        return False

    def retrieve(self, path):
        # Check special cases
        if path == '/':
            if (val := self.app_file.meta_get('app_file_entry_point')) != False:
                path = val
        elif path == '/favicon.ico':
            if (val := self.app_file.meta_get('app_file_favicon')) != False:
                path = val

        # Retrieve the file for a given path
        if (file_data := self.file_from_path(path)) != False:
            return file_data

        # Retrieve custom 404 page, if applicable
        if (path := self.app_file.meta_get('app_file_404_page')) != False:
            if (file_data := self.file_from_path(path)) != False:
                return file_data

        # Otherwise, return the default 404 page
        return b'<html><head><title>404</title></head><body><h1>404</h1></body></html>'

