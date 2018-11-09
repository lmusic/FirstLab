from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import json
import shutil

class MyHttpRequestHandler(BaseHTTPRequestHandler):

    def createFolder(self, dir, name):
            os.mkdir(os.path.join(dir, name))

    def deleteFolder(self, dir, name):
            shutil.rmtree(os.path.join(dir, name))

    def processParamsGet(self, params, dir):
            type = params[0].split("=")[0]
            name = params[0].split("=")[1]
            if type == "create":
                self.createFolder(dir, name)
            if type == "delete":
                self.deleteFolder(dir, name)

    def processNonParamsGet(self, dir):
        if os.path.isdir(dir):
            list = os.listdir(dir)
            json_data = json.dumps(list)
            self.send_response(200)
        if os.path.isfile(dir):
            path = os.path.normpath(dir)
            json_data = open(path, 'rb').read()
            self.send_response(200)
            self.send_header('Content-Disposition', 'attachment')
        self.end_headers()
        self.wfile.write(bytes(json_data,'utf-8'))

    def do_GET(self):
        SERV_DIR = "C:/Users/lmusic/Desktop/MyServFolder"
        json_data = ""
        try:
            params = self.path.split("?")[1].split("&")
            list = self.path.split("?")[0].split("/")
        except:
            params = None
            list = self.path.split("/")
        dir = SERV_DIR
        for item in list:
            if item!="":
                dir = os.path.join(dir, item)
        if params:
            self.processParamsGet(params, dir)

        self.processNonParamsGet(dir)


server_adress = ("", 8000)
httpd = HTTPServer(server_adress, MyHttpRequestHandler)
print("lisenning 8000 port")
httpd.serve_forever()