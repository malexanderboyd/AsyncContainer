from http.server import HTTPServer, SimpleHTTPRequestHandler

def run():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f'Serving on http://localhost:8000')
    httpd.serve_forever()

run()