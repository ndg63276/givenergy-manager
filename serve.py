#!/usr/bin/env python

import sys
if sys.version_info[0] == 3: # python3

	from http.server import HTTPServer, CGIHTTPRequestHandler
else: # python2
	from BaseHTTPServer import HTTPServer
	from CGIHTTPServer import CGIHTTPRequestHandler

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
