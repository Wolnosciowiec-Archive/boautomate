FROM python:3.7-alpine
MAINTAINER RiotKit <riotkit_org@riseup.net>

ADD . /tmp/boautomate
ADD test /data-test
ADD docker/boautomate/entrypoint.py /
ADD defaults/boautomate-local /data/storage
ADD defaults/storage /data/storage

RUN apk add --update bash git docker \
    && addgroup -g 1000 boautomate \
    && adduser -D -s /bin/bash -u 1000 -G boautomate boautomate \
    && mkdir -p /var/log/boautomate/ /var/lib/db /opt/boautomate-workspaces /data/storage /data/config \
    && chown -R boautomate:boautomate /var/log/boautomate/ /var/lib/db /opt/boautomate-workspaces /data \
    \
    # Installation
    \
    && cd /tmp/boautomate \
    && pip install -r ./requirements.txt \
    && python3 ./setup.py install \
    \
    # Entrypoint
    \
    && chmod +x /entrypoint.py \
    \
    # Cleanup
    && rm -rf /tmp/boautomate \
    && rm -rf /var/cache/apk/*

ENV DB_STRING=sqlite:////var/lib/db/database.sqlite3 \
    NODE_MASTER_URL=http://localhost:8080 \
    HTTP_PORT=8080 \
    LOCAL_PATH=/data-test/example-installation/boautomate-local \
    LOG_LEVEL=info \
    LOG_PATH=/var/log/boautomate/boautomate-test.log

USER boautomate

ENTRYPOINT ["/entrypoint.py"]
