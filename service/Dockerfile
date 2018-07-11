FROM python:alpine

MAINTAINER Deutsches Archäologisches Institut "dev@dainst.de"

ENV REFRESHED_AT 2018-03-19

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt
RUN rm /tmp/requirements.txt

EXPOSE 5000

COPY docker-entrypoint.sh /root

ENTRYPOINT ["sh", "/root/docker-entrypoint.sh"]