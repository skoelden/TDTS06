#ifndef __PROXY_CLIENT_H_
#define __PROXY_CLIENT_H_

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <arpa/inet.h>

#include "slre/slre.h"

int process_get_request(char* header_buffer,
                    ssize_t header_lenght,
                    int* content_buffer,
                    int* content_length);

const char* get_hostname_from_get_request(char* header_buffer, int header_length);

#endif
