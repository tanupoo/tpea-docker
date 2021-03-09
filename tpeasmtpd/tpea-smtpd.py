#!/usr/bin/env python3

import sys
import smtpd
import asyncore
import quopri
import email
from html.parser import HTMLParser
import json
from datetime import datetime, timezone, timedelta
import time
import argparse

TPEA_SMTPD_MSG_FILE="/var/log/tpea-smtpd-msg.log"

class MyHTMLParser(HTMLParser):
    '''
    ## Account Activation

    - Account Activation URL

        Encountered a start tag: a
        [('style', 'color:#E36C0A; font-weight: bold; text-decoration: none;'),
        ('href', 'https://....')]
        Encountered some data  : Account Activation

    - Login name

        Encountered some data  : Login: 
        Encountered some data  : sakane@tanu.org

    - Account name

        Encountered some data:[Hi ]
        Encountered some data:[test test]

        the following lines are not used for compatibility to Reset.

        Encountered some data  : Account name: 
        Encountered some data  : test1 test1

    ## Account Reset

    - Account Reset URL

        Encountered a start tag:[a]
        [('style', 'color:#E36C0A; font-weight: bold; text-decoration: none;'),
        ('href', 'https://....')]
        Encountered some data:[Account Reset]

    - Account name

        Encountered some data:[Hi ]
        Encountered some data:[test test]

    '''
    def __init__(self, config):
        self.config = config
        if self.config["debug"]:
            HTMLParser.__init__(self, convert_charrefs = True)
        HTMLParser.__init__(self)
        self.msg_title = None   # Activation or Reset
        self.ac_name = None
        self.ac_login = None
        self.ac_url = None
        self.__href_tmp = None

    def result(self):
        t = datetime.now(tz=timezone(timedelta(0, -time.timezone))).isoformat()
        return {
                "msg_title":self.msg_title,
                "ac_time":t,
                "ac_name":self.ac_name,
                "ac_login":self.ac_login,
                "ac_url":self.ac_url
                }

    def handle_starttag(self, tag, attrs):
        if self.config["debug"]:
            print("Encountered a start tag:[{}]".format(tag))
            print(attrs)
        # get a href anyway.
        if tag == "a":
            for i in attrs:
                if i[0] == "href":
                    if self.__href_tmp is None:
                        self.__href_tmp = i[1]

    def handle_data(self, data):
        '''
        - data includes some charactors unexpected.
        '''
        if self.config["debug"]:
            print("Encountered some data:[{}]".format(data))
        # get Account Name
        if self.ac_name == 1:
            self.ac_name = data.strip()
            return
        '''
        if "Account name:" in data:
            if self.ac_name is None:
                self.ac_name = 1
            else:
                # if exists, just ignore it.
                #raise Exception("Account name exists already.")
                pass
            return
        '''
        if "Hi " in data:
            if self.ac_name is None:
                self.ac_name = 1
            else:
                # if exists, just ignore it.
                #raise Exception("Account name exists already.")
                pass
            return
        # get Login Name
        if self.ac_login == 1:
            self.ac_login = data.strip()
            return
        if "Login:" in data:
            if self.ac_login is None:
                self.ac_login = 1
            else:
                raise Exception("Login name exists already.")
            return
        # get Activation URL
        if self.ac_url == 1:
            self.ac_url = self.__href_tmp.strip()
            return
        if "Account Activation" in data:
            self.msg_title = "Activation"
            if self.ac_url is None:
                self.ac_url = 1
            else:
                raise Exception("Activation URL exists already.")
            return
        # get Activation URL
        if "Account Reset" in data:
            self.msg_title = "Reset"
            if self.ac_url is None:
                self.ac_url = 1
            else:
                raise Exception("Reset URL exists already.")
            return

class CustomSMTPServer(smtpd.SMTPServer):

    def __init__(self, config):
        self.config = config
        super().__init__(config["localaddr"], None)

    def get_html_text(self, msg):
        if msg.is_multipart():
            for i in msg.walk():
                if self.config["debug"]:
                    print(msg.get_boundary(), i.get_content_type())
                    print(i.get_payload(decode=True))
                if i.get_content_type() == "text/html":
                    return i.get_payload(decode=True).decode()
        return None

    def save_msg(self, data):
        if self.config["debug"]:
            print("save msg into", self.config["msg_file"])
            print(data)
        with open(self.config["msg_file"], "a+") as fd:
            fd.write("{} {}\n".format(data["ac_time"],json.dumps(data)))

    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        src = data.decode(encoding="utf-8")
        msg = email.message_from_string(src)
        if self.config["debug"]:
            print("Receiving message from:", peer)
            print("smtp from:", mailfrom)
            print("smtp to  :", rcpttos)
            print("kwargs:", kwargs)
            #print(data)
            print("env from :", msg["from"])
            print("env to   :", msg["to"])
            print("subject  :", msg["subject"])
            print("Message body:")
            print(msg)
        # get the HTML message
        html_text = self.get_html_text(msg)
        if html_text:
            # parse the HTML message. 
            p = MyHTMLParser(self.config)
            p.feed(html_text)
            self.save_msg(p.result())
            p.close()

ap = argparse.ArgumentParser(description="The SMTP server for TPE.")
ap.add_argument("-a", action="store", dest="bind_addr", default="::",
                help="specify the address to be bound.")
ap.add_argument("-p", action="store", dest="bind_port", type=int, default=8825,
                help="specify the port number to be bound.")
ap.add_argument("-m", action="store", dest="msg_file",
                default=TPEA_SMTPD_MSG_FILE,
                help="specify the port number to be bound.")
ap.add_argument("-d", action="store_true", dest="debug",
                help="enable debug mode.")
opt = ap.parse_args()

config = {
        "localaddr":(opt.bind_addr, opt.bind_port),
        "remoteaddr":None,
        "msg_file":opt.msg_file,
        "debug":opt.debug
        }
server = CustomSMTPServer(config)
print("SMTP server has started.  Listen on {} {}".format(
        opt.bind_addr if opt.bind_addr else "any", opt.bind_port))

asyncore.loop()
