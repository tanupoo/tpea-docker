#!/usr/bin/env python3

try:
    # in python3
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from socketserver import ThreadingMixIn
except ImportError:
    # in python2
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
    from SocketServer import ThreadingMixIn

import time
import ssl
import argparse
import mmap
import json

def get_lines(msg_file, n_lines):
    '''
    return a byte type string (which may be multiple lines).
    EOL must be 0x0a.
    '''
    mm = None
    ok = False
    for i in range(5):
        '''
        wait for 5 seconds if the message is written.
        '''
        fd = open(msg_file)
        mm = mmap.mmap(fd.fileno(), 0, prot=mmap.PROT_READ)
        if mm[-1] == 10:
            ok = True
            break
        mm.close()
        fd.close()
        time.sleep(1)
        if True:
            print("the file is not ended by EOL.")
    #
    if not ok:
        raise Exception("the file looks broken.")
    #
    pos = -1
    for i in range(n_lines):
        pos = mm.rfind(b"\n", 0, pos)
        if pos == -1:
            break
    m = mm[1+pos:]
    mm.close()
    fd.close()
    return m

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        '''
        valid path:
            /raw
            /raw/
            /raw/<n>
            /
            /<n>
        '''
        raw_mode = False
        tmp_num = None
        if self.path.startswith("/raw/") and len(self.path) > len("/raw/"):
            tmp_num = self.path[len("/raw/"):]
            raw_mode = True
        elif self.path in ["/raw", "/raw/"]:
            raw_mode = True
        elif self.path.startswith("/") and len(self.path) > len("/"):
            tmp_num = self.path[len("/"):]
        elif self.path == "/":
            pass
        else:
            self.send_response(404)
            return
        #
        if tmp_num:
            try:
                n_lines = int(tmp_num)
            except:
                self.send_response(404)
                return
        else:
            n_lines = self.server.opt.n_lines
        #
        self.send_response(200)
        if raw_mode:
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(get_lines(self.server.opt.msg_file, n_lines))
        else:
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            body = "<html><body><table border=1 cellpadding=3>"
            body += "<thead><tr>"
            body += "<th>Type</th><th>Time</th><th>Name</th><th>Login name</th><th></th>"
            body += "</tr></thead><tbody>"
            lines = get_lines(self.server.opt.msg_file,
                              n_lines).decode().split("\n")
            lines.pop(-1)   # must be "\n"
            for line in lines:
                m = json.loads(line[1+line.index(" "):])
                body += "<tr>"
                body += """
<td>{msg_title}</td>
<td>{ac_time}</td>
<td>{ac_name}</td>
<td>{ac_login}</td>
<td><a href="{ac_url}">Click to accept</a></td>""".format(**m)
                body += "</tr>"
            body += "</tbody></table>"
            body += "* Last {} lines in the log.".format(len(lines))
            body += "</body></html>"
            self.wfile.write(body.encode())

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    '''Handle requests in a separate thread.'''

def test_server(opt):
    try:
        httpd = ThreadedHTTPServer((opt.bind_addr, opt.bind_port), Handler)
        httpd.opt = opt
        httpd.socket = ssl.wrap_socket (httpd.socket,
                                        certfile=opt.cert_file,
                                        server_side=True)
        print("Starting server https://{}:{}".format(
                opt.bind_addr, opt.bind_port))
        print("Use <Ctrl-C> to stop")
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down the server")

ap = argparse.ArgumentParser()
ap.add_argument("-a", action="store", dest="bind_addr", default="0.0.0.0",
                help="specify a hostname to be bound.")
ap.add_argument("-p", action="store", dest="bind_port", type=int, default=8843,
                help="specify a port number to be bound.")
ap.add_argument("-c", action="store", dest="cert_file",
                help="specify a certificate file.")
ap.add_argument("-m", action="store", dest="msg_file",
                help="specify a message file.")
ap.add_argument("-n", action="store", dest="n_lines", type=int, default=2,
                help="specify the number of lines to be read.")

opt = ap.parse_args()
test_server(opt)

