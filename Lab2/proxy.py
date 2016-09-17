import socket
import re
import os

class easy_socket:

    def __init__(self, sock=None):
        if sock == None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self, host, port=80):
        self.sock.connect((host, port))

    def send(self, msg):
        total_sent = 0
        msg_length = len(msg)
        while total_sent < msg_length:
            sent = self.sock.send(msg[total_sent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            total_sent = total_sent + sent

    def receive_http_response(self):
        chunks = []
        bytes_read = 0

        chunk = self.sock.recv(2048)
        chunks.append(chunk)
        bytes_read = bytes_read + len(chunk)

        m = re.search(r'content-length: ([^\s]+)', chunk.lower())
        content_length = int(m.group(1))

        if content_length > bytes_read:
            while bytes_read < content_length:
                chunk = self.sock.recv(min(content_length - bytes_read, 2048))
                chunks.append(chunk)
                bytes_read = bytes_read + len(chunk)

        return ''.join(chunks)

def request_handler(ok_get_request, client_to_proxy_socket):
    # Search header for blocked content

    m = re.search(r'Host: ([^\s]+)', ok_get_request)
    host = m.group(1)
    print("GET request for {}".format(host))

    proxy_to_server_socket = easy_socket()
    proxy_to_server_socket.connect(host=host, port=80)

    proxy_to_server_socket.send(ok_get_request)
    http_response = proxy_to_server_socket.receive_http_response()

    client_to_proxy_socket.send(http_response)

def main():
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversocket.bind(('localhost', 3490))
    serversocket.listen(5)

    while 1:
        (s, address) = serversocket.accept()
       
        
        print("Connected to {}".format(address))
        get_request = s.recv(2048)

        print(get_request)
        if get_request[0:3] != "GET":
            #This is not a GET request, drop it
            break

        # Fork and pass it to the request_handler
        pid = os.fork()
        if pid == 0:
            client_to_proxy_socket = easy_socket(sock=s)
            request_handler(get_request, client_to_proxy_socket)

if __name__ == "__main__":
    main()
