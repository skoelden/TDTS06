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

#    print("Recieving data")
    data = sock.recv(2048)
    if re.search(r'HTTP/\d.\d 30[124]', data):
        return data

 #   print("Packet is of 200 (ish) type")
    header, data = data.split('\r\n\r\n')
    #print(header)
    #print("")
    #print(data)

#    print("Header is: \n{}".format(header))
#    print("Data is: \n{}".format(data))
    header_dict = header_to_dict(header)

    if 'content-length' in header_dict:

        content = [data]
        content_read = len(data)

        content_length = int(header_dict['content-length'])

        if content_length > content_read:
            while content_read < content_length:
                data = sock.recv(min(content_length - content_read, 2048))
                content.append(data)
                content_read = content_read + len(data)

        return serialize_header_dict(header_dict) + ''.join(content)

    elif 'transfer-encoding' in header_dict:

            #print("Data is chunked")
            unchunkified_content = []

            while not data[-5:] == "0\r\n\r\n":
                tmp = sock.recv(2048)
                data += tmp

            chunk_header, data = data.split('\r\n', 1)
            #print("Chunk header is: {}\n".format(repr(chunk_header)))
            #print("Data is now1: \n{}\n".format(repr(data)))

            while not chunk_header == "0":
                # Read an entire chunk
                chunk_size = int(chunk_header, 16)
                #print("chunk_size is: {}".format(chunk_size))

                # We have a full chunk in data
                #print("Appending chunk containing: {}\n".format(repr(data[:chunk_size])))
                unchunkified_content.append(data[:chunk_size])
                data = data[chunk_size+2:]
                #print("Data is now2: \n{}\n".format(repr(data)))
                chunk_header, data = data.split('\r\n', 1)
                #print("Chunk header is: {}".format(repr(chunk_header)))
                #print("Data is now3: \n{}".format(repr(data)))

            content = ''.join(unchunkified_content)

            del header_dict['transfer-encoding']
            header_dict.update({'content-length':str(len(content))})

 #           print(serialize_header_dict(header_dict))
            return serialize_header_dict(header_dict) + content
