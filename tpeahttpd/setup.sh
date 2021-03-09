#!/bin/sh

openssl req -new -x509 -newkey rsa:2048 -days 7300 \
    -out ./etc/server-cert.pem \
    -keyout ./etc/server-cert.pem \
    -nodes -subj '/CN=TPE Assistant'
