# -*- coding: utf-8 -*-
import os
import sys
from flask_sqlalchemy import SQLAlchemy
from app import db
from datetime import datetime
 
class Signup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer,db.ForeignKey('event.id'))
    signedup_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    
    def save(self):
        db.session.add(self)
        db.session.commit()
    
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
    repairman_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    signedupu = db.relationship('Signup',backref='eventup',foreign_keys=[Signup.event_id],lazy='dynamic')
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get(event_id):
        return db.session.query(Event).filter(Event.id == event_id).first()

    @staticmethod
    def get_all():
        return db.session.query(Event).all()
    
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
    events = db.relationship('Event',backref='user',foreign_keys=[Event.user_id],lazy='dynamic')
    repairman = db.relationship('Event',backref='repairman',foreign_keys=[Event.repairman_id],uselist=False)
    signedupe = db.relationship('Signup',backref='userup',foreign_keys=[Signup.signedup_id],lazy='dynamic')
    
    @staticmethod
    def get_by_mail(mail):
        return db.session.query(User).filter(User.email == mail).first()

    def get(user_id):
        return db.session.query(User).filter(User.id == user_id).first()

    def check_password(self, password):
        if self.password == password:
            return True
        return False
    

    
db.create_all()

