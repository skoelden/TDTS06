import re

from collections import OrderedDict

def URL_contains_bad_words(get_request, banned_words):
    for banned_word in banned_words:
        bad_URL = re.search(banned_word, get_request.lower())
        if bad_URL is not None:
            return True

    return False

def content_contains_bad_words(http_response, banned_words):
    header = http_response.split('\r\n\r\n')[0]
    header_dict = header_to_dict(header)

    if 'content-type' in header_dict:
        if header_dict['content-type'].startswith('text'):
            for banned_word in banned_words:
                bad_content = re.search(banned_word, http_response.lower())
                if bad_content is not None:
                    # The content contained bad word(s)
                    return True

    return False

def get_http_version(firstline):
    m = re.search(r'http\/(\d\.\d)', firstline.lower())
    version = m.group(1)
    return version

def header_to_dict(header):
    header_dict = OrderedDict()
    lines = header.split('\r\n')

    header_dict['first_line'] =  lines[0]
    for line in lines[1:]:
        parts = line.split(': ')
        header_dict[parts[0].lower()] = parts[1].lower()

    return header_dict

def serialize_header_dict(header_dict):
    serialized_str = header_dict['first_line'] + '\r\n'

    for key in header_dict.keys():
        if key == 'first_line': continue

        serialized_str += key + ': ' + header_dict[key] + '\r\n'

    serialized_str += '\r\n'

    return serialized_str

def receive_http_response(sock):

        data = sock.recv(2048)
        if re.search(r'HTTP/\d.\d 30[124]', data):
            return data

        header, data = data.split('\r\n\r\n')
        #print(header)
        #print("")
        #print(data)

        header_dict = header_to_dict(header)

        if 'content-length' in header_dict:

            content = data
            content_read = len(data)

            content_length = int(header_dict['content-length'])

            if content_length > content_read:
                while content_read < content_length:
                    data = sock.recv(min(content_length - content_read, 2048))
                    content.append(data)
                    content_read = content_read + len(data)

            return serialize_header_dict(header_dict) + ''.join(content)

        elif 'transfer-encoding' in header_dict:
            if False: #not  header_dict['transfer-encoding'] == 'chunked':
               print("AAAARRRGHHHHHHH, this ain't no transfer-encoding i know about!")
              #  return
            else:

                unchunkified_content = []

                #m_chunk_header = re.match(r'([a-f0-9]*)\r\n', part)
                chunk_header, data = data.split('\r\n')
                print("Nara nu...")
                #print("Header: {}".format(header))
                #print("Chunk header: {}".format(chunk_header))
                #print("Chunk: {}".format(chunk))
                print(chunk_header)
                while not (chunk_header == "" or chunk_header == "0"):
                    # Read an entire chunk
                    chunk_size = int(chunk_header, 16)

                    if len(data) < chunk_size:
                        # Need to fetch more data

                        while len(data) < chunk_size:
                            tmp = sock.recv(2048)
                            data += tmp

                    print(len(data) < chunk_size)
                    # We have a full chunk in data
                    unchunkified_content.append(data[:chunk_size])
                    data = data[chunk_size+2:]
                    chunk_header, data = data.split('\r\n')

                print("Efter while not chunk_header...")
                content = ''.join(unchunkified_content)
                del header_dict['transfer-encoding']
                header_dict['content-length'] = len(content)

                return serialize_header_dict(header_dict) + content
