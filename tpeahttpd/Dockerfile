FROM alpine:3.12
RUN apk add python3=3.8.5-r1
ADD tpea-httpd.py /tpea/tpea-httpd.py
RUN chmod 755 /tpea/tpea-httpd.py
CMD ["/tpea/tpea-httpd.py", "-m", "/work/msg.log", "-c", "/tpea/etc/server-cert.pem", "-a", "0.0.0.0"]
