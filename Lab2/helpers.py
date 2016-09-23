import re

from collections import OrderedDict


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
        if re.search(r'HTTP/\d.\d 30[14]', part):
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
                    part = sock.recv(min(content_length - bytes_read, 2048))
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
                            tmp = sock.recv(2048)

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
