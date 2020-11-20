FROM tensorflow/tensorflow:2.2.1-py3

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r /tmp/requirements.txt

RUN rm /tmp/requirements.txt

EXPOSE 5000

RUN mkdir /service
COPY docker-entrypoint.sh /service
COPY main.py /service 
WORKDIR /service

ENTRYPOINT ["sh", "/service/docker-entrypoint.sh"]