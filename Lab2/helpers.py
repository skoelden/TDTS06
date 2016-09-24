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

        part = sock.recv(2048)
        if re.search(r'HTTP/\d.\d 30[124]', part):
            return part

        print(part)

        m_cl = re.search(r'content-length: ([^\s]+)', part.lower())
        m_te = re.search(r'transfer-encoding: ([^\s]+)', part.lower())

        if m_cl is not None:
            # Header has content length
            parts = []
            content_read = 0

            parts.append(part)
            content_read = content_read + len(part.split('\r\n\r\n')[1])

            content_length = int(m_cl.group(1))

            if content_length > content_read:
                while content_read < content_length:
                    part = sock.recv(min(content_length - content_read, 2048))
                    parts.append(part)
                    content_read = content_read + len(part)

            return ''.join(parts)

        elif m_te is not None:
            if m_te.group(1).lower() != 'chunked':
                print("AAAARRRGHHHHHHH, this ain't no transfer-encoding i know about!")
                return
            else:
                unchunkified_response = []
                header, content = part.split('\r\n\r\n')
                unchunkified_response.append(header)
                unchunkified_response.append('\r\n\r\n')

                #m_chunk_header = re.match(r'([a-f0-9]*)\r\n', part)
                chunk_header, chunk = content.split('\r\n')

                #print("Header: {}".format(header))
                #print("Chunk header: {}".format(chunk_header))
                #print("Chunk: {}".format(chunk))
                

                content_length = 0
                #for i in range(1,3):
                while not chunk_header == "":
                    print(repr(chunk_header))
                    chunk_size = int(chunk_header, 16)
                    print(chunk_size)
                    return
                    content_length += chunk_size

                    if len(part) < chunk_size:
                        chunk = part

                        while True:
                            tmp = sock.recv(2048)

                            if len(chunk) + len(tmp) >= chunk_size:
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
