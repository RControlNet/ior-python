FROM ubuntu:bionic AS builder
RUN apt-get update
RUN apt-get install python3 python3-pip git -y

WORKDIR /ior

RUN git clone https://github.com/RControlNet/rcn-cli.git

FROM python:3.11.0b3-alpine3.16

COPY --from=builder /ior /tmp/

RUN apk add --no-cache --virtual .build-deps gcc musl-dev

WORKDIR /tmp/rcn-cli
RUN pip3 install -r requirements.txt
RUN pip3 install .


WORKDIR /ior

COPY ../ior_research ior_research
COPY ../setup.py setup.py
COPY ../setup.cfg setup.cfg
COPY ../README.md README.md

COPY ./requirements.txt requirements.txt
COPY ./dockerfiles/configs configs
COPY ../examples .

RUN pip3 install -r requirements.txt
RUN pip3 install .

RUN apk del .build-deps gcc musl-dev

ENV RCONTROLNETCONFIG=/ior/configs/default.yml
COPY ../resources/receiver.yml resources/receiver.yml

CMD ["python3", "joystick_control/PsJoystickClient.py"]