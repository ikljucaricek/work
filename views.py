# -*- coding: utf-8 -*-

from functools import wraps
from flask import request, render_template, Response, g, session, redirect, url_for, flash, send_from_directory
from app import app
from datetime import datetime
from model import User, Event # from database
from werkzeug import secure_filename

def login_required(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        if not ('id' in session):
            return redirect('/signin')
        return fn(*args, **kwargs)
    return decorated_view

@app.route('/')
def index():
    return render_template('index.html', events = Event.get_all()[:-11:-1])

@app.route('/startup')
@login_required
def startup():
    return render_template('startup.html', username = session['username'], events = Event.get_all()[:-11:-1])

@app.route('/signin', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #username = request.form.get('username')
        mail = request.form.get('mail')
        password = request.form.get('lozinka')
        user = User.get_by_mail(mail)
        if user and user.check_password(password):
            session['id'] = user.id
            session['username'] = user.username
        else:
            flash('You entered wrong data!')
            return redirect('/signin')
        flash('Hello ' + user.name + ' ' + user.surename + '!')
        return render_template('startup.html', username=user.username, events = Event.get_all()[:-11:-1])
    else:
        return redirect('/')

@app.route('/signout')
@login_required
def logout():
    session.pop('username', None)
    session.pop('id', None)
    return redirect('/')

@app.route('/startup')
@login_required
def start():
    return render_template('startup.html')

@app.route('/createvent', methods=['GET', 'POST'])
@login_required
def create_an_event():
    if request.method == 'POST':
        path_to_photo = None
        #if request.form.get('datmtme') >= datetime.now():
        if 'photo' in request.files:
            photo = request.files['photo']
            extension = photo.filename.split('.')
            #Needs to be revised
            path_to_photo = './static/images/events_photos/' + secure_filename(str(session['id']) + '.' + extension[-1])
            photo.save(path_to_photo)

        event = Event(
            name = request.form.get('name'),
            description = request.form.get('description'),
            price = request.form.get('price'),
            address = request.form.get('address'),
            date_time_create = datetime.now(),
            date_time_close = request.form.get('datmtme'),
            accessories_purchased = request.form.get('accessories'),
            user_id = session.get('id'),
            active = 1,
            photo = path_to_photo)
        event.save()
        flash('You have successfully created Event!')
    #flash('Event cannot be completed before it starts')
    return render_template('startup.html', username = session['username'])

@app.route('/profile/<username>')
def profilePage(username):
    user = User.get_by_username(username)
    #user_photo = user.picture
    return render_template('profile.html', user = user)

@app.route('/modifyuser', methods=['GET', 'POST'])
@login_required
def modify_an_user():
    if request.method == 'POST':
        path_to_photo = None
        user_n = User.get_by_username(session['username'])
        #if request.form.get('datmtme') >= datetime.now():
        if 'photo' in request.files:
            photo = request.files['photo']
            extension = photo.filename.split('.')
            #Needs to be revised
            path_to_photo = './static/images/users_avatar/' + secure_filename(str(session['id']) + '.' + extension[-1])
            photo.save(path_to_photo)

        user = User(
            id = session['id'],
            name = request.form.get('name'),
            surename = request.form.get('surname'),
            username = request.form.get('username'),
            address = request.form.get('address'),
            email = request.form.get('email'),
            mobile = request.form.get('mobile'),
            picture = path_to_photo)
        user.modify()
        flash('You successfully modified Event!')
    #flash('Event cannot be completed before it starts')
    return render_template('profile.html', user = user_n)

@app.route('/events')
@login_required
def allevents():
    return render_template('events.html', username = session['username'], events = Event.get_all()[::-1])