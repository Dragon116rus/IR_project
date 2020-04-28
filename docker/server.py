import json
import re
import io
import pickle
import glob
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import librosa

import shazam

PORT_NUMBER = 8080

class shazamHandler(BaseHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super(BaseHTTPRequestHandler, self).__init__(*args, **kwargs)


    def do_POST(self):
        content_len = int(self.headers.get('content-length'))
        post_body = self.rfile.read(content_len)
        with open("tmp/tmp.mp3", "wb") as f:
            f.write(post_body)
        wav, _ = librosa.load("tmp/tmp.mp3",
                              shazam.sample_rate,
                              duration=shazam.time_to_process)
        predict = shazam.predict(wav, index)
        json_ = str(json.dumps(predict))+"\n"

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

def load_indexes():
    data_all = {}
    index_files = glob.glob("volumes/index*.pckl")
    print("Index files:", index_files)
    for i in (index_files):
        with open(i, "rb") as f:
            data = pickle.load(f)
        for key in data:
            if key in data_all:
                data_all[key] += data[key]
            else:
                data_all[key] = data[key]
        print("Loaded:", i)
    return data_all

if __name__ == "__main__":
    index = load_indexes()
    if len(index)==0:
        print("No index")
        sys.exit()

    try:
        # Create a web server and define the handler to manage the
        # incoming request
        server = ThreadingHTTPServer(('', PORT_NUMBER), shazamHandler)
        print('Started http-server on port ', PORT_NUMBER)

        # Wait forever for incoming htto requests
        server.serve_forever()

    except KeyboardInterrupt:
        print('^C received, shutting down the web server')
        server.socket.close()
