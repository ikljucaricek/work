# -*- coding: utf-8 -*-

from functools import wraps
from flask import request, render_template, Response, g, session, redirect, url_for, flash
from app import app
from model import User, Event # from database

def login_required(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        if not ('id' in session):
            return redirect('/signin')
        return fn(*args, **kwargs)
    return decorated_view

@app.route('/')
def index():
    return render_template('index.html')

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
            flash('Unijeli ste pogresne podatke za prijavu!')
            return redirect('/signin')
        flash('Hello ' + user.name + ' ' + user.surename + '!')
        return render_template('startup.html', user=user)
    else:
        return render_template('signin.html')

@app.route('/signout')
def logout():
    session.pop('username', None)
    session.pop('id', None)
    return redirect('/signin')

@app.route('/startup')
@login_required
def start():
    return render_template('startup.html')