from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import base64
import numpy as np
import cv2
from model import Model


model = Model()


class MyHandler(BaseHTTPRequestHandler):

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_OPTIONS(self):
        logging.info("OPTIONS request,\nPath: %s\nHeaders:\n%s\n",
                     str(self.path), str(self.headers))
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', '*')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

    def do_GET(self):
        logging.info("GET request\nHeaders:\n%s\n", str(self.headers))
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n",
                     str(self.path), str(self.headers))
        encoded_data = post_data.split(',')[1]
        nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
        # Make raw image from URI
        img_raw = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        name, box = model.detect(img_raw)
        im = np.array(cv2.imencode('.png', img_raw)[1]).tobytes()
        data64 = base64.b64encode(im).decode('utf-8')
        res = f'{{"img": "data:image/jpeg;base64,{data64}", "name": "{name}", "box": [{box[0]}, {box[1]}, {box[2]}, {box[3]}]}}'
        self._set_response()
        self.wfile.write(res.encode('utf-8'))


def run():
    logging.basicConfig(level=logging.INFO)
    server_address = ('', 8080)
    server_class = HTTPServer
    handler_class = MyHandler
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')


if __name__ == '__main__':
    run()
