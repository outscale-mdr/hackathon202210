#!/bin/sh

set -e

SSH_PRIVATE_KEY="~/.ssh/hackathon.rsa"

app1ip=$(cat ./app1_connect.sh | sed 's/.*@\([.0-9]*\)/\1/')
db1ip=$(cat ./db1_connect.sh | sed 's/.*@\([.0-9]*\)/\1/')
ms1ip=$(cat ./ms1_connect.sh | sed 's/.*@\([.0-9]*\)/\1/')

echo "Syncing app1"
scp -o StrictHostKeyChecking=no -i "$SSH_PRIVATE_KEY" app1/src/* outscale@${app1ip}:/data/code
ssh -o StrictHostKeyChecking=no -i "$SSH_PRIVATE_KEY" outscale@${app1ip} sudo systemctl restart app1.service

echo "Syncing db1"

echo "Syncing ms1"
scp -o StrictHostKeyChecking=no -i "$SSH_PRIVATE_KEY" ms1/src/* outscale@${ms1ip}:
ssh -o StrictHostKeyChecking=no -i "$SSH_PRIVATE_KEY" outscale@${ms1ip} sudo systemctl restart ms1.service
