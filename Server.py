import socket
import threading
import argparse
import time
from random import randint
import sys


class Server:

    connections = []
    users = []

    def __init__(self, host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen(1)

        print("Connection established on", host, ":", port)
        establish()
        while True:
            connection, address = sock.accept()

            host = address[0]
            port = address[1]

            connectionThread = threading.Thread(
                target=self.handler, args=(connection, address))
            connectionThread.daemon = True
            connectionThread.start()

            self.connections.append(connection)
            self.users.append(host)
            print(str(host) + ':' + str(port), 'connected')
            print("Total connections: ", len(self.users))
            self.sendUsers()

    def handler(self, connection, address):

        while True:
            data = connection.recv(1024)
            for self.connection in self.connections:
                self.connection.send(data)

            # client disconnected
            if not data:
                host = address[0]
                port = address[1]

                print(str(host) + ':' + str(port), 'disconnected')
                self.connections.remove(connection)
                self.users.remove(host)
                connection.close()
                self.sendUsers()
                print("Total connections: ", len(self.users))
                break

    def sendUsers(self):
        u = ""
        for user in self.users:
            u = u + user + ","
        for connection in self.connections:
            connection.send(b'\x11' + bytes(u, "utf-8"))

    def broadcast(self):
        print('hi')


def establish():
    threading.Timer(2.0, establish).start()
    print("Server running..")


# Helper function to see if we can connect
def connect(host, port):

    if host == None:
        return False

    if port == None:
        return False

    if host and port:
        return True


if __name__ == "__main__":

    # Parsing the passed in argyments
    parser = argparse.ArgumentParser()
    parser.add_argument("-H", "--host", type=str)
    parser.add_argument("-P", "--port", type=int)
    args = parser.parse_args()

    # extract port & host from args
    host = args.host
    port = args.port

    if host and port:
        try:
            server = Server(host, port)
            establish()
        except KeyboardInterrupt:
            sys.exit(0)
    else:
        print('Please provide a host and a port, -H , -P')
        sys.exit(0)
