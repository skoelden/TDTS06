import socket
import re
import os
import sys

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

        part = self.sock.recv(2048)
        if re.search(r'HTTP/\d.\d 30[124]', part):
            return part

        m_cl = re.search(r'content-length: ([^\s]+)', part.lower())
        m_te = re.search(r'transfer-encoding: ([^\s]+)', part.lower())

        if m_cl is not None:
            # Header has content length
            parts = []
            bytes_read = 0

            parts.append(part)
            bytes_read = bytes_read + len(part)

            content_length = int(m_cl.group(1))

            if content_length > bytes_read:
                while bytes_read < content_length:
                    part = self.sock.recv(min(content_length - bytes_read, 2048))
                    parts.append(part)
                    bytes_read = bytes_read + len(part)

            return ''.join(parts)

        elif m_te is not None:
            if m_te.group(1).lower() != 'chunked':
                print("AAAARRRGHHHHHHH, this ain't no transfer-encoding i know about!")
                return
            else:
                unchunkified_response = []
                # Find end of header
                m_eoh = re.search(r'(\r\n\r\n)', part)
                header_length = m_eoh.end(1)
                unchunkified_response.append(part[:header_length])

                part = part[header_length:]
                m_chunk_header = re.match(r'([a-f0-9]*)\r\n', part)
                part = part[m_chunk_header.end(0):]

                content_length = 0
                #for i in range(1,3):
                while  m_chunk_header.group(1) != "":
                    chunk_size = int(m_chunk_header.group(1), 16)
                    content_length += chunk_size

                    if len(part) < chunk_size:
                        chunk = part

                        while True:
                            tmp = self.sock.recv(2048)

                            if len(chunk) + len(tmp) > chunk_size:
                                break

                            chunk += tmp

                        part = chunk + tmp # part now contatins the full chunk

                    unchunkified_response.append(part[:chunk_size])
                    part = part[chunk_size:]
                    m_chunk_header = re.match(r'([a-f0-9]*)\r\n', part)

                response = ''.join(unchunkified_response)
                response = re.sub(r'[Tt]ransfer-[Ee]ncoding: chunked', 'Content-length: {}'.format(content_length), response)
                #print(response)
                return response

    def recv(self, num):
        self.sock.recv(num)

    def getpeername(self):
        self.sock.getpeername()

    def settimeout(self, num):
        self.sock.settimeout(num)

def search_URL(get_request):
    bad_URL = re.search('spongebob', get_request.lower())
    if bad_URL is not None:
        return True
    else:
        return False

def search_content(http_response):
    #if "insert Eriks coola tabellfunktion" == "text/html":
    bad_content = re.search('spongebob', http_response.lower())
    if bad_content is not None:
            # The content contained bad word(s)
        return True
    else:
        return False
    #else:
     #   return False

def request_handler(s):
    get_request = s.recv(2048)

    client_to_proxy_socket = easy_socket(sock=s)

    while True:
        #print(get_request)
        """if get_request[0:3] != "GET":
            #This is not a GET request, drop it
            print("AAAARRRGHHHHHHH, this ain't no GET request!")
            print(get_request)
            client_to_proxy_socket.shutdown()
            client_to_proxy_socket.close()
            return"""
        print get_request

        # Search header for blocked content

        if search_URL(get_request):
            print("Bad URL")
            response = "HTTP/1.1 302 Found\r\nLocation: http://www.ida.liu.se/~TDTS04/labs/2011/ass2/error1.html\r\nHost: http://www.ida.liu.se\r\n\r\n"
            client_to_proxy_socket.send(response)
            bad_URL = None
            return
        else:
            print("Good URL")
            host = get_host(get_request)
            bad_URL = None


        # Remove the host from get request first line
        get_request = re.sub('(?P<get>GET) http://' + host + '(?P<path>.+) ', '\g<get> \g<path> ',get_request)



        print("GET request for {}".format(host))

        proxy_to_server_socket = easy_socket()
        proxy_to_server_socket.connect(host=host, port=80)

        proxy_to_server_socket.send(get_request)
        http_response = proxy_to_server_socket.receive_http_response()
        proxy_to_server_socket.shutdown()
        proxy_to_server_socket.close()

        # Search for blocked content


        if search_content(http_response):
            print("Bad content")
            response = "HTTP/1.1 302 Found\r\nLocation: http://www.ida.liu.se/~TDTS04/labs/2011/ass2/error2.html\r\nHost: http://www.ida.liu.se\r\n\r\n"
            client_to_proxy_socket.send(response)
            bad_content = None
        else:
            print("Good content")

        client_to_proxy_socket.send(http_response)

        http_version = get_http_version(get_request)
        if http_version == '1.0':
            client_to_proxy_socket.shutdown()
            client_to_proxy_socket.close()
            return
        else:
            client_to_proxy_socket.send(http_response)
            m_conn = re.search(r'[Cc]onnection: (\w+-\w+)', http_response)

            if m_conn != None:
                if m_conn.group(1).lower() == 'keep-alive':
                    client_to_proxy_socket.settimeout(10)
                    try:
                        get_request = s.recv(2048)
                    except socket.timeout:
                        client_to_proxy_socket.shutdown()
                        client_to_proxy_socket.close()
                        return
                else:
                    client_to_proxy_socket.shutdown()
                    client_to_proxy_socket.close()
                    return


def get_http_version(get_request):
    m = re.search(r'http\/(\d\.\d)', get_request.lower())
    version = m.group(1)
    return version

def get_host(get_request):
    m = re.search(r'host: ([^\s]+)', get_request.lower())
    host = m.group(1)
    return host

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
    elif int(sys.argv[1]) >= port_min and int(sys.argv[1]) <= port_max:
        port = int(sys.argv[1])
        print("Port: {}".format(port))
    else:
        port = 3490
        print("Invalid port, default port: {}".format(port))

    serversocket.bind(('localhost', port))
    serversocket.listen(5)

    while 1:
        (s, address) = serversocket.accept()

        print("Connected to {}".format(address))

        # Fork and pass it to the request_handler
        pid = os.fork()
        if pid == 0:
            serversocket.close()
            request_handler(s)
            break
        else:
            s.close()

if __name__ == "__main__":
    main()
