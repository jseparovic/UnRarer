#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"


if [[ "$1" == "" ]]
then
    echo "Usage: $0 SCAN_PATH"
    echo "Eg: $0 /mnt/torrents/completed"
    exit 1
fi

SCAN_PATH=${1}
SERVICE=unrarer

# check dir exists
if [[ ! -d ${SCAN_PATH} ]]
then
    echo "Scan path ${SCAN_PATH} does not exist"
    exit 2
fi

# write PATH to config file
cat << EOF > /etc/unrarer.conf
[main]
SCAN_PATH=${SCAN_PATH}
EOF

# requires python daemons configparser to be installed
easy_install-3 daemons configparser || exit 1

# install unrar
yum install unrar -y

cd ${DIR}
mkdir -p /usr/local/bin
mkdir -p /var/lib/${SERVICE}
/bin/cp -f ${SERVICE}.py /var/lib/${SERVICE}
/bin/cp -rf libs /var/lib/${SERVICE}
/bin/cp -f ${SERVICE}.service  /etc/systemd/system/
systemctl daemon-reload
systemctl enable ${SERVICE}
systemctl restart ${SERVICE}
sleep 1
systemctl status ${SERVICE}

