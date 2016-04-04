# -*- coding: utf-8 -*-
import os
import sys
from flask_sqlalchemy import SQLAlchemy
from app import db
from datetime import datetime
 
class Applied_repairman(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer,db.ForeignKey('event.id'))
    repairman_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    
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
    signedupe = db.relationship('Applied_repairman',backref='eventup',foreign_keys=[Applied_repairman.event_id],lazy='dynamic')

        #Needs to be revised
    def modify(self):
        #our_user = User.query.filter_by(id=id).first()
        #our_user = User.query.get(id)
        our_event = db.session.query(Event).get(self.id)
        our_event.name = self.name
        our_event.description = self.description
        our_event.price = self.price
        our_event.address = self.address
        our_event.photo = self.photo
        our_event.date_time_close = self.date_time_close
        db.session.add(our_event)
        db.session.commit()
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get(event_id):
        return db.session.query(Event).filter(Event.id == event_id).first()

    @staticmethod
    def get_all():
        return db.session.query(Event).all()

    @staticmethod
    def get_by_name(filter_name):
        return db.session.query(Event).filter(Event.name == filter_name)
    
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
    repairman = db.relationship('Event',backref='repairman',foreign_keys=[Event.repairman_id],lazy='dynamic')
    signedupu = db.relationship('Applied_repairman',backref='userup',foreign_keys=[Applied_repairman.repairman_id],lazy='dynamic')
    
    #Needs to be revised
    def modify(self):
        #our_user = User.query.filter_by(id=id).first()
        #our_user = User.query.get(id)
        our_user = db.session.query(User).get(self.id)
        our_user.name = self.name
        our_user.surename = self.surename
        our_user.mobile = self.mobile
        our_user.address = self.address
        our_user.picture = self.picture
        db.session.add(our_user)
        db.session.commit()

    @staticmethod
    def get_by_mail(mail):
        return db.session.query(User).filter(User.email == mail).first()
        
    @staticmethod
    def get_by_username(username):
        return db.session.query(User).filter(User.username == username).first()

    def get(user_id):
        return db.session.query(User).filter(User.id == user_id).first()

    def check_password(self, password):
        if self.password == password:
            return True
        return False
        
    def save(self):
        db.session.add(self)
        db.session.commit()
    

    
db.create_all()

