FROM python:3.7-alpine

ADD boautomate /opt/
ADD requirements.txt /

RUN apk add --update bash \
    && addgroup -g 1000 boautomate \
    && adduser -D -s /bin/bash -u 1000 -G boautomate boautomate \
    && pip install -r requirements.txt

USER boautomate
