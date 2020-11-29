import http.server
import re
import socketserver
import sqlite3
import threading


def sanitize(sql):
    return ''.join(c for c in sql if c.isalnum())


class FileRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        data = self.server.retrieve(self.path)
        self.wfile.write(data)

        return


class AppFileServer(socketserver.TCPServer):
    def __init__(self, filename, port=8123, *args, **kwargs):
        self.filename = filename
        self.conn = None
        self.curs = None
        self.port = port
        self.running = False
        self.listener_thread = None
        super().__init__(('', self.port), FileRequestHandler)
    
    def serve_forever(self):
        self.conn = sqlite3.connect(self.filename)
        self.curs = self.conn.cursor()

        while self.running:
            self.handle_request()

        self.curs.close()
        self.conn.close()
    
    def file_from_path(self, path):
        if match := re.match(r'/(\w+)/([\w\.]+)', path):
            table = sanitize(match.group(1))
            filename = match.group(2)

            self.curs.execute(f'SELECT data FROM {table} WHERE filename=?', (filename,))
            if data := self.curs.fetchone():
                return data[0]
        
        return False
    
    def retrieve(self, path):
        # Check if we're at the entry point
        if path == '/':
            self.curs.execute(f'SELECT value FROM meta WHERE key="app_file_entry_point"')
            if data := self.curs.fetchone():
                path = data[0]
        
        # Retrieve the file for a given path
        if (file_data := self.file_from_path(path)) != False:
            return file_data
        
        # Retrieve custom 404 page, if applicable
        self.curs.execute(f'SELECT value FROM meta WHERE key="app_file_404_page"')
        if data := self.curs.fetchone():
            path = data[0]

            if (file_data := self.file_from_path(path)) != False:
                return file_data
        
        # Otherwise, return the default 404 page
        return b'<html><head><title>404</title></head><body><h1>404</h1></body></html>'
    
    def start(self):
        self.listener_thread = threading.Thread(target=self.serve_forever)
        self.running = True
        self.listener_thread.start()
    
    def stop(self):
        if self.running and self.listener_thread:
            self.server_close()
            self.running = False
            self.listener_thread.join()