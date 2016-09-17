all: proxy

proxy: proxy.c proxy_client.c proxy_client.h
	gcc -o proxy proxy.c proxy_client.c slre/slre.c;

clean:
	rm proxy
