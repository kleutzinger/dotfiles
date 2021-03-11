#!/usr/bin/env python
import http.server
import socketserver
import sys

if len(sys.argv) > 1:
    PORT = int(sys.argv[1])
else:
    PORT = 8080
print(f"listening on http://0.0.0.0:{PORT}")


class quietServer(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


with socketserver.TCPServer(("", PORT), quietServer) as httpd:
    httpd.serve_forever()
