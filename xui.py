import base64
import json
import os
import secrets
import string
from dataclasses import dataclass
from urllib import parse
from uuid import uuid4

import requests


def generate_password():
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for i in range(15))


class Xui:
    def __init__(
        self,
        ip,
        domain,
        remark="",
        user="admin",
        password="admin",
        port=54321,
        ssl_enabled=False,
        cert_path="/root/cert.crt",
        private_path="/root/private.key",
    ):
        self.ip = ip
        self.domain = domain
        self.port = port
        self.cert_path = cert_path
        self.private_path = private_path
        self.ssl_enabled = ssl_enabled
        self.user = user
        self.password = password
        self.remark = remark
        self.session = None

        self.login()

    @property
    def headers(self):
        return {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": self.host,
            "Pragma": "no-cache",
            "Sec-GPC": "1",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
        }

    @property
    def host(self):
        if not self.ssl_enabled:
            return f"http://{self.ip}:{self.port}"

        return f"https://{self.domain}:{self.port}"

    @property
    def cookies(self):
        return {
            "lang": "en-US",
            "session": self.session,
        }

    def post(self, url, *args, **kwargs):
        _url = parse.urljoin(self.host, url)
        return requests.post(
            _url, *args, headers=self.headers, cookies=self.cookies, **kwargs
        )

    def login(self):
        data = {
            "username": self.user,
            "password": self.password,
        }

        response = self.post("/login", data=data)

        if not response.json()["success"]:
            raise Exception("Invalid user or password")

        set_cookie = response.headers.get("Set-Cookie")
        self.session = set_cookie[len("session=") : set_cookie.find(";")]

    def setup_ssl(self):
        data = {
            "webListen": "",
            "webPort": str(self.port),
            "webCertFile": self.cert_path,
            "webKeyFile": self.private_path,
            "webBasePath": "/",
            "tgBotEnable": "false",
            "tgBotToken": "",
            "tgBotChatId": "0",
            "tgRunTime": "",
            "xrayTemplateConfig": '{\n  "log": {\n    "loglevel": "warning", \n    "access": "./access.log"\n  },\n \n  "api": {\n    "services": [\n      "HandlerService",\n      "LoggerService",\n      "StatsService"\n    ],\n    "tag": "api"\n  },\n  "inbounds": [\n    {\n      "listen": "127.0.0.1",\n      "port": 62789,\n      "protocol": "dokodemo-door",\n      "settings": {\n        "address": "127.0.0.1"\n      },\n      "tag": "api"\n    }\n  ],\n  "outbounds": [\n    {\n      "protocol": "freedom",\n      "settings": {}\n    },\n    {\n      "protocol": "blackhole",\n      "settings": {},\n      "tag": "blocked"\n    }\n  ],\n  "policy": {\n    "levels": {\n      "0": {\n        "statsUserUplink": true,\n        "statsUserDownlink": true\n      }\n    },\n    "system": {\n      "statsInboundDownlink": true,\n      "statsInboundUplink": true\n    }\n  },\n  "routing": {\n    "rules": [\n      {\n        "inboundTag": [\n          "api"\n        ],\n        "outboundTag": "api",\n        "type": "field"\n      },\n      {\n        "ip": [\n          "geoip:private"\n        ],\n        "outboundTag": "blocked",\n        "type": "field"\n      },\n      {\n        "outboundTag": "blocked",\n        "protocol": [\n          "bittorrent"\n        ],\n        "type": "field"\n      }\n    ]\n  },\n  "stats": {}\n}\n',
            "timeLocation": "Asia/Shanghai",
        }

        response = self.post("/xui/setting/update", data=data, verify=False,)
        self.ssl_enabled = True
        print("Restart x-ui to apply ssl")

    def change_password(self, new_password):
        data = {
            "oldUsername": self.user,
            "oldPassword": self.password,
            "newUsername": self.user,
            "newPassword": new_password,
        }

        response = self.post("/xui/setting/updateUser", data=data)
        self.password = new_password

    def add_vmess(self, port, path="ws"):
        uuid = str(uuid4())
        _path = "/" + path
        name = self.remark + '_' + "VMess"

        data = {
            "up": "0",
            "down": "0",
            "total": "0",
            "remark": name,
            "enable": "true",
            "expiryTime": "0",
            "listen": "",
            "port": str(port),
            "protocol": "vmess",
            "settings": '{\n  "clients": [\n    {\n      "id": "%s",\n      "alterId": 0,\n      "email": "",\n      "limitIp": 0,\n      "totalGB": 0,\n      "expiryTime": ""\n    }\n  ],\n  "disableInsecureEncryption": false\n}'
            % uuid,
            "streamSettings": '{\n  "network": "ws",\n  "security": "none",\n  "wsSettings": {\n    "acceptProxyProtocol": false,\n    "path": "%s",\n    "headers": {}\n  }\n}'
            % _path,
            "sniffing": '{\n  "enabled": true,\n  "destOverride": [\n    "http",\n    "tls"\n  ]\n}',
        }

        response = self.post("/xui/inbound/add", data=data)
        config = {
            "add": self.domain,
            "aid": "0",
            "alpn":"",
            "host": self.domain,
            "id": str(uuid),
            "net": "ws",
            "path": _path,
            "port": port,
            "ps": name,
            "scy": "aes-128-gcm",
            "tls": "none",
            "sni":"",
            "type":"",
            "v": "2",
        }
        link = (
            "vmess://"
            + base64.b64encode(
                json.dumps(config, sort_keys=True).encode("utf-8")
            ).decode()
        )
        print(link)

    def add_vless_tls(self, port, path="ws"):
        uuid = str(uuid4())
        _path = "/" + path
        name = self.remark + '_' + "VLess-TLS"

        data = {
            "up": "0",
            "down": "0",
            "total": "0",
            "remark": name,
            "enable": "true",
            "expiryTime": "0",
            "listen": "",
            "port": str(port),
            "protocol": "vless",
            "settings": '{\n "clients": [\n {\n "id": "%s",\n "flow": "xtls-rprx-direct",\n "email": "",\n "limitIp": 0,\n "totalGB": 0,\n "expiryTime": ""\n }\n ],\n "decryption": "none",\n "fallbacks": []\n}'
            % uuid,
            "streamSettings": '{\n "network": "ws",\n "security": "tls",\n "tlsSettings": {\n "serverName": "%s",\n "certificates": [\n {\n "certificateFile": "%s",\n "keyFile": "%s"\n }\n ],\n "alpn": []\n },\n "wsSettings": {\n "acceptProxyProtocol": false,\n "path": "%s",\n "headers": {}\n }\n}'
            % (self.domain, self.cert_path, self.private_path, _path),
            "sniffing": '{\n "enabled": true,\n "destOverride": [\n "http",\n "tls"\n ]\n}',
        }

        response = self.post("/xui/inbound/add", data=data)
        link = f"vless://{uuid}@{self.domain}:{port}?path={parse.quote_plus(_path)}&security=tls&encryption=none&type=ws&sni={self.domain}#{parse.quote_plus(name)}"
        print(link)

    def add_trojan(self, port):
        password = generate_password()
        name = self.remark + '_' + "Trojan"

        data = {
            "up": "0",
            "down": "0",
            "total": "0",
            "remark": name,
            "enable": "true",
            "expiryTime": "0",
            "listen": "",
            "port": port,
            "protocol": "trojan",
            "settings": '{\n  "clients": [\n    {\n      "password": "%s",\n      "flow": "xtls-rprx-direct"\n    }\n  ],\n  "fallbacks": []\n}'
            % password,
            "streamSettings": '{\n  "network": "tcp",\n  "security": "tls",\n  "tlsSettings": {\n    "serverName": "%s",\n    "certificates": [\n      {\n        "certificateFile": "%s",\n        "keyFile": "%s"\n      }\n    ],\n    "alpn": []\n  },\n  "tcpSettings": {\n    "acceptProxyProtocol": false,\n    "header": {\n      "type": "none"\n    }\n  }\n}'
            % (self.domain, self.cert_path, self.private_path),
            "sniffing": '{\n  "enabled": true,\n  "destOverride": [\n    "http",\n    "tls"\n  ]\n}',
        }
        response = self.post("/xui/inbound/add", data=data)
        link = f"trojan://{password}@{self.domain}:{port}?sni={self.domain}#{parse.quote_plus(name)}"
        print(link)
