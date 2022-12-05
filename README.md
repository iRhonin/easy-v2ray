# Easy X-UI Script

Install and Config a V2Ray server with one script

## Prerequisites

- A Domain
- A VPS with **root access** and Debian Based OS (Ubuntu, Debian, ...)
- Python >= 3.8
- Linux

## Usage

### 1. Set a A DNS Record to your VPS's IP

For example:

`yourdomain.com >> 1.2.3.4 (Your VPS IP)`

\*If you using Cloudflare or ArvanCloud or similar services, **MAKE SURE THE CLOUD FLAG IS DISABLED**!

### 2. Clone this repo

```bash
git clone https://github.com/iRhonin/easy-v2ray.git
```

### 3. Set variables

Copy `.env.example` to `.env` and set the variables.

```bash
cp .env.example .env
# Edit .env
```

### 4. Run Script

```bash
/bin/sh install.sh
```

### 5. Done!

You now have VMess, VLess-TLS and Trojan configs!

Install a [client](https://github.com/XTLS/Xray-core#gui-clients) and enjoy!
