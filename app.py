# -*- coding: utf-8 -*-
import logging, os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.secret_key = '26s3uqr&v2@dt@93%*79biuao@)zlmmi)^^p*jycr#!&ydg_ok7l78'
if os.environ.get('DATABASE_URL') is None:
	app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://workuser:work1234@localhost/work'
else:
	app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
#pp.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://nwbzhqmswnhfuh:MKkoYXy-J-ig_ezQLfKB-c2eMI@ec2-23-23-107-82.compute-1.amazonaws.com:5432/dcsg94fhfj1fne'

db = SQLAlchemy(app)

from views import *


if __name__ == "__main__":
    logging.basicConfig(filename='logs.log', level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler())
#    app.run(debug=True, host="0.0.0.0")
	app.run()