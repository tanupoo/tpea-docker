tpeasmtpd
===========

## Dockerfile

```
FROM alpine:3.12
RUN apk add python3=3.8.5-r1
ADD tpea-smtpd.py /tpea/tpea-smtpd.py
RUN chmod 755 /tpea/tpea-smtpd.py
CMD ["/tpea/tpea-smtpd.py", "-m", "/tpea/work/msg.log"]
```

## build

```
docker build --tag tpeasmtpd:0.1 .
```

## configure

## run

```
docker run \
    --name tpeasmtpd \
    --volume tpea_work:/tpea/work \
    --publish 8825:8825 \
    micro:tpeasmtpd \
    /tpea/tpea-smtpd.py -m /tpea/work/msg.log
```

## check

