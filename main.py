import server
import tools

if __name__ == '__main__':
    # tools.db_create('test.db')
    # tools.db_verify('test.db')

    app_server = server.AppFileServer('test.db')
    app_server.start()
    input()
    app_server.stop()