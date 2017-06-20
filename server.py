# -*- coding:utf-8 -*-

from http.server import BaseHTTPRequestHandler, HTTPServer
import uestc_misc as uestc


def start_server(PORT=23333):
    http_server = HTTPServer(('', int(PORT)), Server)
    http_server.serve_forever()


class Server(BaseHTTPRequestHandler):

    def do_GET(self):
        #print(self.path)

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        username, password = self.get_para()
        print(username,password)
        if username is None:
            response = {
                'code':'-1',
                'msg':'can\'t find username!',
            }
            self.wfile.write(bytes(str(response),encoding='utf-8'))
            return
        if password is None:
            response = {
                'code': '-1',
                'msg': 'can\'t find password!',
            }
            self.wfile.write(bytes(str(response), encoding='utf-8'))
            return
        try:
            course = self.get_course(username, password)
        except uestc.LoginError:
            response = {
                'code': '-1',
                'msg': 'username or password is wrong!',
            }
            self.wfile.write(bytes(str(response), encoding='utf-8'))
            return

        self.wfile.write(bytes(str(course), encoding='utf-8'))

    def get_course(self, username, password):
        user = uestc.uestc_user(username, password)
        return uestc.course_info(user)

    def get_para(self):
        path = str(self.path)
        if 'username=' not in path:
            return None, None
        if 'password=' not in path:
            return None, None
        username = path[path.index('username=')+len('username='):path.index('&')]
        password = path[path.index('password=')+len('password='):len(path)]
        return username, password