from flask import request, render_template, Response, g, session, redirect, url_for
from app import app
from models import User, Event # from database

@app.route('/')
def index():
    return render_template('index.html')