import os
import sys
from flask_sqlalchemy import SQLAlchemy
from app import db
from datetime import datetime 
 
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    surename = db.Column(db.String(250),nullable=False)
    username = db.Column(db.String(250), nullable=False,unique=True)
    password = db.Column(db.String(250),nullable=False)
    picture = db.Column(db.LargeBinary)
    email = db.Column(db.String(250),nullable=False,unique=True)
    mobile = db.Column(db.String(15))
    address = db.Column(db.String(250))
    rating = db.Column(db.Float)
    joindate = db.Column(db.DateTime)
    
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    photo = db.Column(db.LargeBinary)
    active = db.Column(db.Boolean)
    price = db.Column(db.Float,nullable=False)
    address = db.Column(db.String(250),nullable=False)
    date_time_create = db.Column(db.DateTime)
    date_time_close = db.Column(db.DateTime)
    accessories_purchased = db.Column(db.Boolean)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    repairman_id = db.Column(db.Integer)
    
db.create_all()
