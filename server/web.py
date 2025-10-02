from http.server import HTTPServer, SimpleHTTPRequestHandler


class RequestHandler(SimpleHTTPRequestHandler):
    ''' 自定义 handler '''
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write('<h1>hello, world</h1>'.encode())


server = HTTPServer(('', 8000), RequestHandler)
server.serve_forever()
