#include "proxy_client.h"

int process_get_request(char* header_buffer,
                    ssize_t header_length,
                    int* content_buffer,
                    int* content_length){

  char* host = get_hostname_from_get_request(header_buffer, (int)header_length);
  struct addrinfo hints, *clientinfo, *p;
  int client_socket;
  int status;
  int yes = 1;
  
  memset(&hints, 0, sizeof hints); // make sure the struct is empty
  hints.ai_family = AF_INET;       // we want IPv4
  hints.ai_socktype = SOCK_STREAM; // TCP stream sockets
  // hints.ai_flags = AI_PASSIVE;     // fill in my IP for me
  
  if ((status = getaddrinfo(host, "80", &hints, &clientinfo)) != 0) {
    fprintf(stderr, "getaddrinfo error: %s\n", gai_strerror(status));
    exit(1);
  }

  for (p = clientinfo; p != NULL; p = p->ai_next) {
    if ((client_socket = socket(p->ai_family, p->ai_socktype,
                               p->ai_protocol)) == -1) {
      perror("server: socket");
      continue;
    }

    if (setsockopt(client_socket, SOL_SOCKET, SO_REUSEADDR, &yes,
                   sizeof(int)) == -1) {
      perror("setsockopt");
      exit(1);
    }

    if ((connect(client_socket, clientinfo->ai_addr, clientinfo->ai_addrlen)) == -1) {
      close(client_socket);
      perror("server: bind");
      continue;
    }

    break;
  }

  freeaddrinfo(clientinfo);

  int content_buffer_len = (int)powl(2, 20); //One MB buffer
  content_buffer = malloc(content_buffer_len);
  printf(inet_addr(clientinfo->ai_addr));
  send(client_socket, header_buffer, header_length, 0);

}


const char* get_hostname_from_get_request(char* header_buffer, int header_length){

  struct slre_cap caps[1];
  if(slre_match("Host: ([^\r\n]+)", header_buffer, header_length, caps, 1, 0)){

    char* host = malloc(caps[0].len + 1);
    strncpy(host, caps[0].ptr, caps[0].len);
    host[caps[0].len + 1] = '\0';
    return host;

  } else{

    perror("No host in GET request");
    exit(0);

  }

}
