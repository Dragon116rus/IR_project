import requests
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json

PORT_NUMBER = 8080
servers = []
score_threshold = 50

class shazamProxyHandler(BaseHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super(BaseHTTPRequestHandler, self).__init__(*args, **kwargs)

    @staticmethod
    def collect_responses(post_data):
        responses = []
        for ip in servers:
            r = requests.post(ip, data=post_data)
            responses.append(r.content.decode())
        return responses

    @staticmethod
    def decode_jsons(data):
        result = []
        for d in data:
            result+= json.loads(d)
        return result

    @staticmethod
    def filter_by_score(data):
        data.sort(key=lambda x: -x['Score'])
        if data[0]['Score']<score_threshold:
            return [data[0]]
        return [d for d in data if d['Score']>score_threshold]

    def do_POST(self):
        content_len = int(self.headers.get('content-length'))
        post_body = self.rfile.read(content_len)

        responses = self.collect_responses(post_body)
        responses = self.decode_jsons(responses)
        responses = self.filter_by_score(responses)
        print(responses)
        json_ = json.dumps(responses)

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        self.wfile.write(json_.encode())

    # Handler for the GET requests
    def do_GET(self):
        self.send_response(404)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        response_str = ""
        self.wfile.write(response_str.encode())
        return

def load_mappers():
    with open("volumes/servers.cfg") as f:
        servers = f.readlines()
        servers = [server.rstrip() for server in servers]
    return servers



if __name__ == "__main__":
    servers = load_mappers()
    print(servers)
    try:
        # Create a web server and define the handler to manage the
        # incoming request
        server = ThreadingHTTPServer(('', PORT_NUMBER), shazamProxyHandler)
        print('Started http-server on port ', PORT_NUMBER)

        # Wait forever for incoming http requests
        server.serve_forever()

    except KeyboardInterrupt:
        print('^C received, shutting down the web server')
        server.socket.close()
