# Easy X-UI Script

Install and Config a V2Ray server with one script

## Prerequisites

- A Domain
- A VPS with **root access** and Debian Based OS (Ubuntu, Debian, ...)
- Docker

## Usage

### Set a A DNS Record to your VPS's IP

For example:

`yourdomain.com >> 1.2.3.4 (Your VPS IP)`

\*If you using Cloudflare or ArvanCloud or similar services, **MAKE SURE THE CLOUD FLAG IS DISABLED!**

#### Run with Docker

Make sure you have installed docker, if not get it from (here)[https://docs.docker.com/get-docker/].

```bash
docker run \
    -e IP="1.1.1.1" `# Change this` \
    -e PASSWORD="password" `# Change this` \
    -e DOMAIN="domain.com" `# Change this` \
    -e REMARK="proxy_" `# Change this` \
    -e USER="root" \
    -e XPORT="54321" \
    -e XUSER="admin" \
    -e XPASSWORD="admin" \
    -e SSL_ENABLED="FALSE" \
    -e CERT_PATH="/root/cert.crt" \
    -e PRIVATE_PATH="/root/private.key" \
    ghcr.io/irhonin/easy-v2ray:latest
```

You now have VMess, VLess-TLS and Trojan configs!

Install a [client](https://github.com/XTLS/Xray-core#gui-clients) and enjoy!

---

### Run Manually on Ubuntu or Debian based OSs

### Clone this repo

```bash
git clone https://github.com/iRhonin/easy-v2ray.git
```

### Install sshpass

```bash
sudo apt install sshpass -y
```

### Set variables

Copy `.env.example` to `.env` and set the variables.

```bash
cp .env.example .env
# Edit .env
```

### Run Script

```bash
/bin/sh install.sh
```
