#!/bin/sh

#python3 manage.py runserver 0.0.0.0:8000
python3 manage.py runsslserver --certificate fullchain.pem --key privkey.pem  0.0.0.0:8000
