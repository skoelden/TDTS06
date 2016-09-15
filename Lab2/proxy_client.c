#include "proxy_client.h"

process_get_request(int* header_buffer,
                    ssize_t header_lenght,
                    int* content_buffer,
                    int* content_length){

  get_hostname_from_get_request(header_buffer)
}

const char* get_hostname_from_get_request(int* header_buffer){
  regex_t regex;

  if(regcomp(&regex, "Host: (.+)\n", 0)){
    perror("Could not compile regex.");
    exit(1);
  }

}
