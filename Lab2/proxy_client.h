#ifndef __PROXY_CLIENT_H_
#define __PROXY_CLIENT_H_

#include <regex.h>

process_get_request(int* header_buffer,
                    ssize_t header_lenght,
                    int* content_buffer,
                    int* content_length)

const char* get_hostname_from_get_request(int* header_buffer)

#endif
