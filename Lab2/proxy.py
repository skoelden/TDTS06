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

    def shutdown(self, how=socket.SHUT_RDWR):
        self.sock.shutdown(how)

    def close(self):
        self.sock.close()

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
        print(chunk)
        chunks.append(chunk)
        bytes_read = bytes_read + len(chunk)

        m_cl = re.search(r'content-length: ([^\s]+)', chunk.lower())
        m_te = re.search(r'transfer-encoding: ([^\s]+)', chunk.lower())
        if m_cl is not None:
            # Header has content length
            content_length = int(m_cl.group(1))

            if content_length > bytes_read:
                while bytes_read < content_length:
                    chunk = self.sock.recv(min(content_length - bytes_read, 2048))
                    chunks.append(chunk)
                    bytes_read = bytes_read + len(chunk)

        elif m_te is not None:
            #print(chunk)
            return

        return ''.join(chunks)

    def recv(self, num):
        self.sock.recv(num)

    def getpeername(self):
        self.sock.getpeername()

def request_handler(s):
    get_request = s.recv(2048)

    client_to_proxy_socket = easy_socket(sock=s)

    print(get_request)
    if get_request[0:3] != "GET":
        #This is not a GET request, drop it
        print("AAAARRRGHHHHHHH, this ain't no GET request!")
        print(get_request)
        client_to_proxy_socket.shutdown()
        client_to_proxy_socket.close()
        return

    # Search header for blocked content

    host = get_host(get_request)
    print("GET request for {}".format(host))

    proxy_to_server_socket = easy_socket()
    proxy_to_server_socket.connect(host=host, port=80)

    proxy_to_server_socket.send(get_request)
    http_response = proxy_to_server_socket.receive_http_response()
    proxy_to_server_socket.shutdown()
    proxy_to_server_socket.close()

    http_version = get_http_version(get_request)
    if http_version == '1.0':
        client_to_proxy_socket.send(http_response)
        client_to_proxy_socket.shutdown()
        client_to_proxy_socket.close()
        return
    else:
        client_to_proxy_socket.send(http_response)
        client_to_proxy_socket.shutdown()
        client_to_proxy_socket.close()
        return
        # Check connection type
        # Mabye, get timeout value
        # Mabye, set timer
        # wait


def get_http_version(get_request):
    m = re.search(r'http\/(\d\.\d)', get_request.lower())
    version = m.group(1)
    return version

def get_host(get_request):
    m = re.search(r'host: ([^\s]+)', get_request.lower())
    host = m.group(1)
    return host

def main():
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversocket.bind(('localhost', 3490))
    serversocket.listen(5)

    while 1:
        (s, address) = serversocket.accept()

        print("Connected to {}".format(address))

        # Fork and pass it to the request_handler
        #pid = os.fork()
        #if pid == 0:
            #serversocket.close()
        request_handler(s)
         #   break
        #else:
            #s.close()

if __name__ == "__main__":
    main()
