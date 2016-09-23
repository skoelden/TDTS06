import socket
import re
import os
import sys

from simple_sock import simple_sock
from request_handler import request_handler

def main():
    #port = sys.argv[1]
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Set the port, valid ports are between port_min and port_max
    port_min = 1024
    port_max = 65535
    if len(sys.argv) < 2:
        port = 3490
        print("No port given, default port: {}".format(port))
    elif int(sys.argv[1]) >= 1024 and int(sys.argv[1]) <= 100000:
        port = int(sys.argv[1])
        print("Port: {}".format(port))
    else:
        port = 3490
        print("Invalid port, default port: {}".format(port))

    serversocket.bind(('localhost', port))
    serversocket.listen(5)

    while 1:
        (s, address) = serversocket.accept()

        print("Spawning new thread")
        new_request = request_handler(s)
        new_request.run()

if __name__ == "__main__":
    main()
