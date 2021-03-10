tpea docker
===========

## install docker-compose

```
apt install docker docker-compose
```

after installation, you may add the user to the docker group.
for example, let's say *tpea* as the user name.

```
sudo usermod -a -G docker tpea
```

the, logout and login to enalbe geting the privilege.

## clone tpea-docker.

```
git clone https://github.com/tanupoo/tpea-docker
cd tpea-docker
docker-compose build
```

now current directory is called $TPEA_DIR from here.
you can set it as an env variable.

```
export TPEA_DIR=`pwd`
```

configure chrony.conf.

```
cp chronyd/etc/chrony.conf.template chronyd/etc/chrony.conf
```

set allow directive.  e.g. allow 192.168.1.0/24.
if you don't mind that the server accepts queries from any clients.  you can use *all* ALLOW_HOSTS.

you may add to proper NTP server's address.
for example, replace from NTP_SERVER such *133.243.238.164*.

```
echo allow ALLOW_HOSTS >> chronyd/etc/chrony.conf
echo server NTP_SERVER offline >> chronyd/etc/chrony.conf
```

make the http server's certificate.

```
(cd tpeahttpd && ./setup.sh)
```

## systemd

replace WorkingDirectory to TPE_DIR.
Note that you have to replace $TPE_DIR into the current directory.

```
WorkingDirectory=$TPE_DIR
```

```
cp docker-compose-app.service /etc/systemd/system/
```

```
systemctl start docker-compose-app
systemctl enable docker-compose-app
```

```
systemctl status docker-compose-app
```

