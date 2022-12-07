#!/bin/sh

set -e

if [ -f .env ]; then
    export $(cat .env)
fi


PASSWORD_FILE=.password
echo $PASSWORD | sed 's/"//g' > .password

cleanup() {
  rm  -r $PASSWORD_FILE
}

trap cleanup EXIT

ssh_ () {
    sshpass -f $PASSWORD_FILE ssh -o StrictHostKeychecking=no -o PubkeyAuthentication=false -t $USER@$IP $1
}



# Install deps
ssh_ "apt install curl socat fail2ban -y"
echo "Installed depps"

# Install Acme Script
ssh_ "curl https://get.acme.sh | sh"
echo "Install Acme Script"

# Get Free SSL Certificate using Let’s Encrypt
ssh_ "~/.acme.sh/acme.sh --set-default-ca --server letsencrypt"
ssh_ "~/.acme.sh/acme.sh --register-account -m xxxx@xxxx.com"
ssh_ "~/.acme.sh/acme.sh --issue -d $DOMAIN --standalone"
ssh_ "~/.acme.sh/acme.sh --installcert -d $DOMAIN --key-file /root/private.key --fullchain-file /root/cert.crt"

echo "Got Free SSL Certificate using Let’s Encrypt"

# Optimizing
ssh_ \
   "curl https://raw.githubusercontent.com/iRhonin/easy-v2ray/master/sysctl/local.conf -o /etc/sysctl.d/local.conf && sysctl --system"

# Install X-UI
ssh_ "echo 'n' | bash <(curl -Ls https://raw.githubusercontent.com/hossinasaadi/x-ui/master/install.sh)"
echo "Installed X-UI"

# Setup venv
python3 -m venv .venv
. .venv/bin/activate
pip3 install -r requirements.txt
echo "Setup venv"

# Setup ssl
python3 cli.py setup-ssl
SSL_ENABLED=TRUE
echo "Setup SSL"

# Restart x-ui
ssh_ "x-ui restart"
echo "Restart x-ui"

sleep 3

# Change password
xui=$(python3 cli.py change-password)
echo $xui
XPASSWORD=$(echo $xui  | grep -Po '(?<=PASSWORD: )[^ ]*')

# # Install cron job to restart x-ui every 12 hours, due to memory leak
# ssh_ 'cat <(crontab -l) <(echo "0 1 * * * /usr/bin/x-ui restart") | crontab -'
# echo "cron job installed"

# Setup configs
python3 cli.py add-vmess 80 ws
python3 cli.py add-vless-tls 443 wss
python3 cli.py add-trojan 995

