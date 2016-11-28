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
    
    @staticmethod
    def get_link(event_id, repairman_id):
        return db.session.query(Applied_repairman).filter(Applied_repairman.event_id == event_id and Applied_repairman.repairman_id == repairman_id).first()
        # here is a potential source of the problem, in general it should be ".all()" in the end but then the views needs to operate with a list 
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        
class Event_comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer,db.ForeignKey('event.id'))
    comment = db.Column(db.String(255),nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    date_time_post = db.Column(db.DateTime)
    
    def save(self):
        db.session.add(self)
        db.session.commit()
            
    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    tag_description = db.Column(db.String(255))

    def save(self):
        db.session.add(self)
        db.session.commit()
        
        
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    photo = db.Column(db.LargeBinary)
    active = db.Column(db.Boolean)
    closed = db.Column(db.Boolean)
    price = db.Column(db.Float,nullable=False)
    city = db.Column(db.String(250),nullable=False)
    neighborhood = db.Column(db.String(250))
    address = db.Column(db.String(250),nullable=False)
    rate = db.Column(db.Integer)
    date_time_create = db.Column(db.DateTime)
    date_time_execute = db.Column(db.DateTime)
    date_time_close = db.Column(db.DateTime)
    accessories_purchased = db.Column(db.Boolean)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    repairman_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    signedupe = db.relationship('Applied_repairman',backref='eventup',foreign_keys=[Applied_repairman.event_id],lazy='dynamic')
    comment = db.relationship('Event_comment',backref='eventcomm',foreign_keys=[Event_comment.event_id],lazy='dynamic')
    tag = db.relationship('Tag', backref = 'event', lazy='dynamic')
        #Needs to be revised
    def modify(self):
        #our_user = User.query.filter_by(id=id).first()
        #our_user = User.query.get(id)
        our_event = db.session.query(Event).get(self.id)
        our_event.name = self.name
        our_event.description = self.description
        our_event.accessories_purchased = self.accessories_purchased
        our_event.price = self.price
        our_event.city = self.city
        our_event.neighborhood = self.neighborhood
        our_event.address = self.address
        our_event.photo = self.photo
        our_event.date_time_execute = self.date_time_execute
        db.session.add(our_event)
        db.session.commit()

    def deactivate(self):
        our_event = db.session.query(Event).get(self.id)
        our_event.active = self.active
        db.session.add(our_event)
        db.session.commit()
        
    def activate(self):
        our_event = db.session.query(Event).get(self.id)
        our_event.active = 1
        db.session.add(our_event)
        db.session.commit()
        
    def remove_repairman(self):
        our_event = db.session.query(Event).get(self.id)
        our_event.repairman_id = None
        db.session.add(our_event)
        db.session.commit()
        
    def decline(self):
        our_event = db.session.query(Event).get(self.id)
        our_event.active = self.active
        our_event.repairman_id = self.repairman_id
        db.session.add(our_event)
        db.session.commit()

    def close_rate(self):
        our_event = db.session.query(Event).get(self.id)
        our_event.active = self.active
        our_event.closed = self.closed
        our_event.rate = self.rate
        db.session.add(our_event)
        db.session.commit()
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get(event_id):
        return db.session.query(Event).filter(Event.id == event_id).first()

    @staticmethod
    def get_all(page=1):
        result_of_qry = Event.query.paginate(page, 12, False)
        pages = result_of_qry.pages
        return result_of_qry.items[::-1], pages
        #return db.session.query(Event).all()

    @staticmethod
    def get_active_events():
        return db.session.query(Event).filter(Event.active == '1')

    @staticmethod
    def get_closed_events():
        return db.session.query(Event).filter(Event.closed == 1)

    @staticmethod
    def get_by_name_or_description(filter_event, page):
        result_of_query = Event.query.filter(Event.name.like('%' + filter_event + '%') | Event.description.like('%' + filter_event + '%')).paginate(page, 12, False)
        pages = result_of_query.pages
        return result_of_query.items[::-1], pages

    @staticmethod
    def get_repairman_avg_rating(repairman_id):
        results = Event.query.filter(Event.repairman_id == repairman_id)
        sum_for_avg = 0
        counter = 0
        #sum(res.rate > 0 for res in results)
        for res in results:
            if res.rate > 0:
                sum_for_avg = sum_for_avg + res.rate
                counter = counter + 1
        return sum_for_avg / float(counter)

    
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
    comment = db.relationship('Event_comment',backref='usercomm',foreign_keys=[Event_comment.user_id],lazy='dynamic')
    
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

    @staticmethod
    def get(user_id):
        return db.session.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_all():
        return db.session.query(User).all()

    def check_password(self, password):
        if self.password == password:
            return True
        return False

    def save_avg_rating(self):
        repairman = db.session.query(User).get(self.id)
        repairman.rating = self.rating
        db.session.add(repairman)
        db.session.commit()
        
    def save(self):
        db.session.add(self)
        db.session.commit()
  
db.create_all()

