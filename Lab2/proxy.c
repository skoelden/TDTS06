#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <sys/wait.h>
#include <signal.h>

#define BACKLOG 10

void sigchld_handler(int s)
{
    // waitpid() might overwrite errno, so we save and restore it:
    int saved_errno = errno;

    while(waitpid(-1, NULL, WNOHANG) > 0);

    errno = saved_errno;
}


// get sockaddr, IPv4 or IPv6:
void *get_in_addr(struct sockaddr *sa)
{
    if (sa->sa_family == AF_INET) {
        return &(((struct sockaddr_in*)sa)->sin_addr);
    }

    return &(((struct sockaddr_in6*)sa)->sin6_addr);
}

int main(int argc, char **argv)
{
  char* proxy_port;
  int proxy_socket, server_socket, client_socket;
  struct addrinfo hints, *servinfo, *p;
  struct sockaddr_storage their_addr; // connector's address information
  socklen_t sin_size;
  struct sigaction sa;
  int yes=1;
  char s[INET6_ADDRSTRLEN];
  int rv;
  int status;

  // Parse command line argument for port to start the proxy server on
  if (argc == 1) {
    proxy_port = "8080";
  } else if (argc == 2) {
    printf("%i", atoi(argv[1]));
    if (atoi(argv[1]) < 1023) {
      printf("Error! %s not a valid port! Starting on 8080 instead.\n", argv[1]);
      proxy_port = "8080";
    } else {
      proxy_port = argv[1];
    }
  }

  printf("proxy_port is %s\n", proxy_port);

  memset(&hints, 0, sizeof hints); // make sure the struct is empty
  hints.ai_family = AF_INET;       // we want IPv4
  hints.ai_socktype = SOCK_STREAM; // TCP stream sockets
  hints.ai_flags = AI_PASSIVE;     // fill in my IP for me

  if ((status = getaddrinfo(NULL, "3490", &hints, &servinfo)) != 0) {
    fprintf(stderr, "getaddrinfo error: %s\n", gai_strerror(status));
    exit(1);
  }

  // loop through all the results and bind to the first we can
    for (p = servinfo; p != NULL; p = p->ai_next) {
        if ((proxy_socket = socket(p->ai_family, p->ai_socktype,
                p->ai_protocol)) == -1) {
            perror("server: socket");
            continue;
        }

        if (setsockopt(proxy_socket, SOL_SOCKET, SO_REUSEADDR, &yes,
                sizeof(int)) == -1) {
            perror("setsockopt");
            exit(1);
        }

        if (bind(proxy_socket, p->ai_addr, p->ai_addrlen) == -1) {
            close(proxy_socket);
            perror("server: bind");
            continue;
        }

        break;
    }

    freeaddrinfo(servinfo); // all done with this structure

    if (p == NULL)  {
        fprintf(stderr, "server: failed to bind\n");
        exit(1);
    }

    if (listen(proxy_socket, BACKLOG) == -1) {
        perror("listen");
        exit(1);
    }

    sa.sa_handler = sigchld_handler; // reap all dead processes
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = SA_RESTART;
    if (sigaction(SIGCHLD, &sa, NULL) == -1) {
        perror("sigaction");
        exit(1);
    }

    while(1) {  // main accept() loop
        sin_size = sizeof their_addr;
        server_socket = accept(proxy_socket, (struct sockaddr *)&their_addr, &sin_size);
        if (server_socket == -1) {
            perror("accept");
            continue;
        }

        if (!connect(server_socket, (struct sockaddr *)&their_addr, sin_size)){
          perror("failed to connect proxy_socket");
            exit(1);
          }

        // get client IP adress
        inet_ntop(their_addr.ss_family,
            get_in_addr((struct sockaddr *)&their_addr),
            s, sizeof s);
        printf("server: got connection from %s\n", s);

        if (!fork()) { // this is the child process
          close(proxy_socket); // child doesn't need the listener

            void* message_buffer;
            int message_buffer_len = 100000;
            ssize_t bytes_recieved;

            message_buffer = calloc(message_buffer_len, sizeof(char));
            if (message_buffer_len == -1){
              perror("Failed to allocate memory");
              exit(1);
            }

            bytes_recieved = recv(server_socket, message_buffer, message_buffer_len, 0);
            if (bytes_recieved == -1){
              perror("failed to receive data from client");
                exit(1);
            }
            printf(message_buffer);
            if (send(server_socket, message_buffer, bytes_recieved, 0) == -1)
                perror("send");
            close(server_socket);
            exit(1);
            }

            close(server_socket);  // parent doesn't need this
    }

  return 1;
}
