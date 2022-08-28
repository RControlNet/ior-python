FROM ubuntu:bionic AS builder
RUN apt-get update --fix-missing && apt-get install python3 python3-pip git -y --fix-missing

WORKDIR /tmp

RUN git clone https://github.com/RControlNet/rcn-cli.git

FROM python:3.11.0b3-alpine3.16
COPY --from=builder /tmp /tmp/

RUN apk add --no-cache --virtual .build-deps gcc musl-dev

WORKDIR /tmp/rcn-cli
RUN pip3 install -r requirements.txt
RUN pip3 install .

WORKDIR /tmp/ior-python

COPY ./ior_research ior_research
COPY ./setup.py setup.py
COPY ./setup.cfg setup.cfg
COPY ./README.md README.md

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt
RUN pip3 install .

RUN apk del .build-deps gcc musl-dev

WORKDIR /tmp

RUN rm -rf /tmp/*

WORKDIR /ior
COPY ./main.py /ior/app.py
CMD ["python3", "./app.py"]