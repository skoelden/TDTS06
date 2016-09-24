import socket
import threading
import re


from helpers import *

threadLimiter = threading.BoundedSemaphore(8)

class request_handler(threading.Thread):

    def __init__(self, s, banned_words):
        threading.Thread.__init__(self)
        self.client_to_proxy_socket = s
        self.banned_words = banned_words

    def run(self):
        threadLimiter.acquire()
        try:
            self.get_request = self.client_to_proxy_socket.recv(2048)

            self.get_request_dict = header_to_dict(self.get_request.split('\r\n\r\n')[0])

            if not self.get_request_dict['first_line'][0:3] == "GET":
                #This is not a GET request, drop it
                self.client_to_proxy_socket.close()
                return

            if URL_contains_bad_words(self.get_request, self.banned_words):
                print("Bad URL for host {}: {}".format(self.get_request_dict['host'],
                                                       self.get_request_dict['first_line']))
                self.http_response = "HTTP/1.1 302 Found\r\nLocation: http://www.ida.liu.se/~TDTS04/labs/2011/ass2/error1.html\r\nHost: http://www.ida.liu.se\r\nConnection: close\r\n\r\n"
            else:
                # Remove the host from get request first line
                self.get_request_dict['first_line'] = \
                re.sub('(?P<get>GET) .*' + self.get_request_dict['host'] + \
                       '(?P<path>.+) ', '\g<get> \g<path> ', self.get_request_dict['first_line'])


                self.get_request_dict['connection'] = 'close'
                #self.get_request_dict['accept-encoding'] = ""

                self.proxy_to_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.proxy_to_server_socket.connect((self.get_request_dict['host'], 80))

                self.proxy_to_server_socket.sendall(serialize_header_dict(self.get_request_dict))

                self.http_response = receive_http_response(self.proxy_to_server_socket)

                self.proxy_to_server_socket.close()

            if self.http_response is not None:
                if content_contains_bad_words(self.http_response, self.banned_words):
                    print("Bad content for host {}".format(self.get_request_dict['host']))
                    self.http_response = "HTTP/1.1 302 Found\r\nLocation: http://www.ida.liu.se/~TDTS04/labs/2011/ass2/error2.html\r\nHost: http://www.ida.liu.se\r\nConnection: close\r\n\r\n"



                self.client_to_proxy_socket.sendall(self.http_response)

            self.client_to_proxy_socket.close()
        finally:
         threadLimiter.release()
         return
