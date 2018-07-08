#!/bin/sh

python3 -m gunicorn.app.wsgiapp --certfile fullchain.pem --keyfile privkey.pem  bot:run_fb_webhook
