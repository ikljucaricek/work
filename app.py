# -*- coding: utf-8 -*-
import logging
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.secret_key = '26s3uqr&v2@dt@93%*79biuao@)zlmmi)^^p*jycr#!&ydg_ok7l78'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://workuser:work1234@localhost/work'

db = SQLAlchemy(app)

from views import *


if __name__ == "__main__":
    logging.basicConfig(filename='logs.log', level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler())
    app.run(debug=True, host="0.0.0.0")