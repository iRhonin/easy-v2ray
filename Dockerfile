from python:3.8-slim-buster

RUN apt update
RUN apt install sshpass -y
RUN apt clean autoremove

WORKDIR /easy-v2ray
COPY . /easy-v2ray/

CMD ["./install.sh"]
