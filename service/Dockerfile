FROM python:alpine

MAINTAINER Deutsches Archäologisches Institut "dev@dainst.de"

ENV REFRESHED_AT 2018-03-19

RUN apk add --update build-base python-dev mysql-dev

COPY requirements.txt /tmp/requirements.txt
# Installing numpy takes ages, so I moved it outside of the requirements.txt. Otherwise you would have to wait each time
# a new dependency is added.
RUN pip3 install numpy
RUN pip3 install -r /tmp/requirements.txt
RUN rm /tmp/requirements.txt

EXPOSE 5000

COPY docker-entrypoint.sh /root

ENTRYPOINT ["sh", "/root/docker-entrypoint.sh"]