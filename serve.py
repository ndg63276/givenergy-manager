#!/usr/bin/env python3

import sys
from http.server import HTTPServer, CGIHTTPRequestHandler

if len(sys.argv) > 1:
	port = int(sys.argv[1])
else:
	port = 8000

server = HTTPServer
handler = CGIHTTPRequestHandler
server_address = ("", port)
handler.cgi_directories = ["/cgi-bin"]
httpd = server(server_address, handler)

httpd.serve_forever()
