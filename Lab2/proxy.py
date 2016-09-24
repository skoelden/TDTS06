#!/usr/bin/python2

import socket
import re
import os
import sys

from request_handler import request_handler

def main():

    # Set the port, valid ports are between port_min and port_max
    port_min = 1024
    port_max = 65535
    if len(sys.argv) < 2:
        port = 3490
        print("No port given, default port: {}".format(port))
    elif int(sys.argv[1]) >= port_min and int(sys.argv[1]) <= port_max:
        port = int(sys.argv[1])
        print("Port: {}".format(port))
    else:
        port = 3490
        print("Invalid port, default port: {}".format(port))


    banned_words = []
    try:
        banned_words_file = open('banned_words.txt', 'r')
        for line in banned_words_file:
            banned_words.append(line[:len(line) - 1])
    except IOError:
        print("No file named banned_words.txt found, no filtering will occur!")

    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversocket.bind(('localhost', port))
    serversocket.listen(5)

    while 1:
        (s, address) = serversocket.accept()

        new_request = request_handler(s, banned_words)
        new_request.start()

if __name__ == "__main__":
    main()
