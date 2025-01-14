from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sys
from pathlib import Path


from embeddings import embed_message

class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Get content length and read body
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            body = self.rfile.read(content_length)
            try:
                # Parse message JSON
                message = json.loads(body)
                
                # Call embed_message with the received message
                embed_message(message)

                # Send success response
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {'status': 'ok', 'message': 'Message embedded successfully'}
                self.wfile.write(json.dumps(response).encode())
                
            except json.JSONDecodeError:
                # Handle invalid JSON
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {'status': 'error', 'message': 'Invalid JSON payload'}
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                # Handle other errors
                self.send_response(500)
                self.send_header('Content-Type', 'application/json') 
                self.end_headers()
                response = {'status': 'error', 'message': str(e)}
                self.wfile.write(json.dumps(response).encode())
    
    def do_GET(self):
        # Return method not allowed for GET
        self.send_response(405)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        response = {'status': 'error', 'message': 'Method not allowed'}
        self.wfile.write(json.dumps(response).encode())

    do_PUT = do_GET
    do_DELETE = do_GET

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f"Server running on port {port}")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
