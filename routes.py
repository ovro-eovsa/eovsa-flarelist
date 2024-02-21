#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from flask import Flask
from core import eovsa_bundle
import socket
import os

hostname = socket.gethostname()

if hostname == "ovsa":
    app = Flask(__name__, static_folder='/var/www/html/flarelist/static', static_url_path='/flarelist/static')
else:
    app = Flask(__name__)

secret_key_hex = os.getenv('FLARE_FLASK_SECRET_KEY')
app.secret_key = bytes.fromhex(secret_key_hex)

bundles=eovsa_bundle.set_bundles(app)


#include blueprints below
from blueprints.example import example
app.register_blueprint(example)

#include more below
#from blueprints.example2 import example2
#app.register_blueprint(ior_manager)

