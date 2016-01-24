from flask import request, render_template, Response, g, session, redirect, url_for
from app import app
from model import User, Event # from database

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signin')
def login():
	return render_template('signin.html')