import socket
import threading
import re


from helpers import *
from simple_sock import simple_sock

class request_handler(threading.Thread):

    def __init__(self, s):
        self.client_to_proxy_socket = s

    def run(self):

        get_request = self.client_to_proxy_socket.recv(2048)

        get_request_dict = header_to_dict(get_request.split('\r\n\r\n')[0])

        while True:
            if not get_request_dict['first_line'][0:3] == "GET":
                #This is not a GET request, drop it
                print("AAAARRRGHHHHHHH, this ain't no GET request!")
                print(get_request)
                self.client_to_proxy_socket.shutdown(socket.SHUT_RDWR)
                self.client_to_proxy_socket.close()
                return

            # Search header for blocked content
            # Remove the host from get request first line
            print(get_request_dict['first_line'])
            get_request_dict['first_line'] = re.sub('(?P<get>GET) .*' + get_request_dict['host'] + \
                                                 '(?P<path>.+) ', '\g<get> \g<path> ',
                                                 get_request_dict['first_line'])
            print(get_request_dict['first_line'])

            self.proxy_to_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.proxy_to_server_socket.connect((get_request_dict['host'], 80))

            get_request_dict['connection'] = 'close'
            get_request_dict['accept-encoding'] = ""

            self.proxy_to_server_socket.sendall(serialize_header_dict(get_request_dict))

            http_response = receive_http_response(self.proxy_to_server_socket)
            self.proxy_to_server_socket.shutdown(socket.SHUT_RDWR)
            self.proxy_to_server_socket.close()

            if http_response is not None:
                self.client_to_proxy_socket.sendall(http_response)

            http_version = get_http_version(get_request)
            if http_version == '1.0':
                self.client_to_proxy_socket.shutdown()
                self.client_to_proxy_socket.close()
                return
            else:
                if 'connection' in  get_request_dict:
                    if get_request_dict['connection'] == 'keep-alive':
                        client_to_proxy_socket.settimeout(10)
                        try:
                            get_request = self.client_to_proxy_socket.recv(2048)
                        except socket.timeout:
                            self.client_to_proxy_socket.shutdown(socket.SHUT_RDWR)
                            self.client_to_proxy_socket.close()
                            return
                    else:
                        self.client_to_proxy_socket.shutdown(socket.SHUT_RDWR)
                        self.client_to_proxy_socket.close()
                        return

