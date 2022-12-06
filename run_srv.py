from server.server import Server

if __name__ == '__main__':
    srv = Server(port=8001)
    srv.listen()