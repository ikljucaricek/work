 # -*- coding: utf-8 -*-
import logging, os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.babel import Babel

app = Flask(__name__)
app.config['BABEL_DEFAULT_LOCALE'] = 'hr'
babel = Babel(app)

app.secret_key = '26s3uqr&v2@dt@93%*79biuao@)zlmmi)^^p*jycr#!&ydg_ok7l78'
if os.environ.get('JAWSDB_MARIA_URL') is None:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://workuser:work1234@localhost:3308/work'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['JAWSDB_MARIA_URL']
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://fglzebctdqphod:aK6qOhgTPt-e2JSQP05DKpes2S@ec2-54-247-185-241.eu-west-1.compute.amazonaws.com:5432/debfq3v7p66b39'

db = SQLAlchemy(app)

from views import *

# if __name__ == "__main__":
#    logging.basicConfig(filename='logs.log', level=logging.DEBUG)
#    logging.getLogger().addHandler(logging.StreamHandler())
#    app.run(debug=False, host="0.0.0.0")
if __name__ == "__main__":
    logging.basicConfig(filename='logs.log', level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler())
    app.run(debug=True, host="0.0.0.0")
