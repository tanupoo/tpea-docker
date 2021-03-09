FROM alpine:3.12
RUN apk add python3=3.8.5-r1
ADD tpea-smtpd.py /tpea/tpea-smtpd.py
RUN chmod 755 /tpea/tpea-smtpd.py
CMD ["/tpea/tpea-smtpd.py", "-m", "/tpea/work/msg.log"]
