tpeahttpd
===========

## Dockerfile

```
FROM alpine:3.12
RUN apk add python3=3.8.5-r1
ADD tpea-httpd.py /tpea/tpea-httpd.py
RUN chmod 755 /tpea/tpea-httpd.py
CMD ["/tpea/tpea-httpd.py", "-m", "/work/msg.log", "-c", "/tpea/etc/server-cert.pem", "-a", "0.0.0.0"]
```

## build

```
docker build --tag tpeahttpd:0.1 .
```

## configure

```
./setup.sh
```

or

```
openssl req -new -x509 -newkey rsa:2048 -days 7300 \
    -out ./etc/server-cert.pem \
    -keyout ./etc/server-cert.pem \
    -nodes -subj '/CN=TPE Assistant' > ./etc/server-cert.pem
```

## run

```
docker run \
    --name tpeahttpd \
    --volume `pwd`/etc:/tpea/etc \
    --volume tpea_work:/tpea/work \
    --publish 8843:8843 \
    tpeahttpd:0.1 \
    /tpea/tpea-httpd.py -m /tpea/work/msg.log -c /tpea/etc/server-cert.pem -a 0.0.0.0 -a 0.0.0.0
```

## check

