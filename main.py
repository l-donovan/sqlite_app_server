from sqlite_app_server import AppFile, AppFileServer
import tools


if __name__ == '__main__':
    with AppFile('test.db') as db:
        with open('favicon.ico', 'rb') as favicon:
            db.file_add('image', 'favicon.ico', favicon.read())
        app_server = AppFileServer(db)
        app_server.serve_forever()
