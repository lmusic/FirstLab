from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import json
import shutil
import mimetypes

class MyHttpRequestHandler(BaseHTTPRequestHandler):

    def createFolder(self, dir, name):
        os.mkdir(os.path.join(dir, name))

    def deleteFolder(self, dir, name):
        if(name != 'MainFolder'):
            shutil.rmtree(os.path.join(dir, name))

    def deleteFile(self, dir):
        os.remove(dir)

    def getPathToFile(self, dir, name):
        path = os.path.join(dir, name)
        if os.path.isfile(path):
            return os.path.normpath(path)
        else:
            return None

    def getPathToDir(self, dir, name):
        path = os.path.join(dir, name)
        if os.path.isdir(path):
            return os.path.normpath(path)
        else:
            return None

    def makeArchive(self, path, name):
        shutil.make_archive(path, 'zip', path)

    def getNameOfFile(self, path):
        return path.split('\\')[-1]

    def processParamsGet(self, params, dir):
            type = params[0].split("=")[0]
            name = params[0].split("=")[1]
            mtype = self.guess_type(dir)
            if type == "create":
                self.createFolder(dir, name)
                self.processNonParamsGet(dir, mtype)
            if type == "delete":
                path = self.getPathToFile(dir, name)
                if path:
                    self.deleteFile(path)
                else:
                    self.deleteFolder(dir, name)
                self.processNonParamsGet(dir, mtype)
            if type == "download":
                path = self.getPathToDir(dir, name)
                if path:
                    self.makeArchive(path, name)
                    json_data = open(path + '.zip', 'rb').read()
                    os.remove(path + '.zip')
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/zip')
                    if ((mtype != 'text/css') & (mtype != 'text/javascript')) | (self.containsSysFile(dir) == False):
                        self.send_header('Content-Disposition', 'attachment; filename='+name+'.zip')
                    self.end_headers()
                    self.wfile.write(json_data)
                else:
                    self.processNonParamsGet(self.getPathToFile(dir, name), self.guess_type(dir))

    def containsSysFile(self, dir):
        arr = dir.split('/')
        for str in arr:
            if(str == 'MainFolder'):
                return True
        return False

    def processNonParamsGet(self, dir, mtype):
        if os.path.isdir(dir):
            list = os.listdir(dir)
            json_data = json.dumps(list)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(bytes(json_data, 'utf-8'))
        if os.path.isfile(dir):
            path = os.path.normpath(dir)
            json_data = open(path, 'rb').read()
            self.send_response(200)
            self.send_header('Content-Type', mtype)
            if ((mtype != 'text/css') & (mtype != 'text/javascript')) | (self.containsSysFile(dir) == False):
                self.send_header('Content-Disposition', 'attachment; filename='+self.getNameOfFile(path))
            self.end_headers()
            self.wfile.write(json_data)

    def openHtml(self, dir):
        path = os.path.join(dir, 'index.html')
        if os.path.isfile(path):
            normPath = os.path.normpath(path)
            data = open(path, 'rb').read()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(data)

    def guess_type(self, dir):
        type = mimetypes.guess_type(dir)
        return type[0]

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
        if(dir == SERV_DIR):
            self.openHtml(dir)
        else:
            if params:
                self.processParamsGet(params, dir)
            else:
               newtype = self.guess_type(dir)
               self.processNonParamsGet(dir, newtype)


server_adress = ("", 8000)
httpd = HTTPServer(server_adress, MyHttpRequestHandler)
print("lisenning 8000 port")
httpd.serve_forever()