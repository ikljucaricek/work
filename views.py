# -*- coding: utf-8 -*-

from functools import wraps
from flask import request, render_template, Response, g, session, redirect, url_for, flash, send_from_directory
from app import app, db
from datetime import datetime
from model import User, Event, Applied_repairman  # from database
from werkzeug import secure_filename
from sqlalchemy.sql import and_, select
from smtplib import SMTP


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
        return render_template('index.html', events = Event.get_all()[:-11:-1])

@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        path_to_photo = None
        #if request.form.get('datmtme') >= datetime.now():
        usernamecheck = User.get_by_username(request.form.get('username'))
        mailcheck = User.get_by_mail(request.form.get('email'))
        if mailcheck != None:
            flash('We are sorry, register was not sucesfull as this email adress is already registered.')
            return render_template('index.html',events = Event.get_all()[:-11:-1])
        elif usernamecheck != None:
            flash('We are sorry, register was not sucesfull as this username is already registered.')
            return render_template('index.html',events = Event.get_all()[:-11:-1])
        else:            
            user = User(
                name = request.form.get('name'),
                surename = request.form.get('surename'),
                username = request.form.get('username'),
                address = request.form.get('address'),
                email = request.form.get('email'),
                password = request.form.get('password'),
                mobile = request.form.get('mobile'),
                joindate = datetime.now())
            user.save()
            
            us = User.get_by_username(user.username)
            print "Tohle je files"
            print request.files
            print request.files.getlist('photo')
            # pho = request.files[0]
            # print pho.filename
            if 'photo' in request.files:
                photo = request.files['photo']
                extension = photo.filename.split('.')
                path_to_photo = '.\\static\\images\\users_avatar\\' + secure_filename(str(us.id) + '.' + extension[-1])
                photo.save(path_to_photo)
                us.picture = path_to_photo
                us.save()
            flash('You have successfully Registered!')
            session['id'] = us.id
            session['username'] = us.username
            fromaddr = 'tygayoinc@gmail.com'
            toaddrs  = us.email
            msg = registration_mail(us)
            username = 'tygayoinc@gmail.com'
            password = 'Work1234'
            server = SMTP("smtp.gmail.com",587)
            server.ehlo()
            server.starttls()
            server.login(username,password)
            server.sendmail(fromaddr, toaddrs, msg)
            server.close()
            return render_template('startup.html', username=us.username, events = Event.get_all()[:-11:-1])
    else:
        return render_template('index.html', events = Event.get_all()[:-11:-1])        

@app.route('/signout')
def logout():
    session.pop('username', None)
    session.pop('id', None)
    return redirect('/')

@app.route('/startup')
@login_required
def start():
    return render_template('startup.html')
    
@app.route('/edetails/<id>')
@login_required
def showevent(id):
    event = db.session.query(Event).get(id)
    if not event:
        abort(404)
    user = db.session.query(User).get(event.user_id)
    if not user:
        abort(404)
    if event.accessories_purchased == 1:     
        accessP = "checked"
    else:
        accessP = ""
    cuserId=session.get('id')
    Signedupusers = None
    already = 0
    # Checking if the user is owner of this event

    if event.user_id == cuserId:
        #If yes, fetch ids of all signedup users for this event
        s2 = select([(Applied_repairman.repairman_id)]).where(
                                        Applied_repairman.event_id == event.id)
        allsignedup = db.engine.execute(s2).fetchall()
        allsignedups = [r[0] for r in allsignedup]
        # Fetch User objects for these ids
        s3 = select([(User)]).where(User.id.in_(allsignedups))
        Signedupusers = db.engine.execute(s3).fetchall()
    else:    
        # Check If the user is already signed up for this event
        s = select([(Applied_repairman.id)]).where(
                                        and_(
                                            Applied_repairman.event_id == event.id,
                                            Applied_repairman.repairman_id == cuserId)
                                        )
        result = db.engine.execute(s).fetchall()
        if len(result) != 0:
            already = 1
            # print "The user is signed up in this events:"
    
    return render_template('edetails.html',username = session['username'],event=event,
                                                                            user=user,
                                                                   users = Signedupusers,
                                                                   already = already,
                                                                   cuserId = cuserId,
                                                                   accessP = accessP)

                                                                   
@app.route('/signup', methods=['POST','GET'])
def signup():
    eventid = request.form.get('event_to_signup')
    if request.method == 'POST':      
        signed = Applied_repairman(
            event_id = eventid,
            repairman_id = session.get('id')
            )
        signed.save()
        flash('You have successfully signed up for the event!')
        id = session.get('id')
        user = User.get(id)    
    return redirect (url_for('myPage',username=user.username))
    
@app.route('/chooserm', methods=['POST'])
def chooserm():
    eventid = request.form.get('event_to_choose')
    rmid = request.form.get('rm_to_choose')
    event = db.session.query(Event).get(eventid)
    client = db.session.query(User).get(event.user_id)
    rm = db.session.query(User).get(rmid)
    rm.repairman.append(event)
    if request.method == 'POST':      
        rm.repairman.append(event)
        event.active = False
        event.save()
        rm.save()
        
        fromaddr = 'tygayoinc@gmail.com'
        toaddrs  = rm.email
        toaddrs_client = client.email
        msg = confirmation_mail('repairman', rm, client, event, eventid)
        msg_client = confirmation_mail('client', rm, client, event, eventid)
        username = 'tygayoinc@gmail.com'
        password = 'Work1234'
        server = SMTP("smtp.gmail.com",587)
        server.ehlo()
        server.starttls()
        server.login(username,password)
        server.sendmail(fromaddr, toaddrs, msg)
        server.sendmail(fromaddr, toaddrs_client, msg_client)
        server.close()
        
        flash('You have successfully chosed a repairman!')
    return redirect (url_for('showevent', id=eventid))
    # return render_template('startup.html', username = session['username'])   
    
@app.route('/createvent', methods=['GET', 'POST'])
@login_required
def create_an_event():
    if request.method == 'POST':
        path_to_photo = None
        #if request.form.get('datmtme') >= datetime.now():
        if 'photo' in request.files:
            photo = request.files['photo']
            extension = photo.filename.split('.')
            path_to_photo = '.\\static\\images\\events_photos\\' + secure_filename(str(session['id']) + '.' + extension[-1])
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
    return redirect (url_for('myPage', username = session['username']))

@app.route('/profile/<username>')
def profilePage(username):
    user = User.get_by_username(username)
    #user_photo = user.picture
    return render_template('profile.html', user = user)  

@app.route('/mypage/<username>')
@login_required
def myPage(username):
    user = User.get_by_username(username)
    sqltxt = select([(Applied_repairman.event_id)]).where(Applied_repairman.repairman_id == user.id)
    allsignedup = db.engine.execute(sqltxt).fetchall()
    allsignedups = [r[0] for r in allsignedup]
    # Fetch Event objects for these ids
    sqltxt2 = select([(Event)]).where(Event.id.in_(allsignedups))
    Signedupuevents = db.engine.execute(sqltxt2).fetchall()

    #Get all events creted by User
    event_created_by_user_query = select([Event]).where(Event.user_id == user.id)
    event_created_by_user = db.engine.execute(event_created_by_user_query).fetchall()
    return render_template('mypage.html', user = user, CreatedEvents = event_created_by_user, SUPevents = Signedupuevents)   

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
        flash('You successfully modified Profile!')
    #flash('Event cannot be completed before it starts')
    return render_template('profile.html', user = user_n)

@app.route('/modifyevent', methods=['GET', 'POST'])
@login_required
def modify_an_event():
    if request.method == 'POST':
        path_to_photo = None
        user_n = User.get_by_username(session['username'])
        originid = request.form.get('id')
        originEvent = Event.get(originid)
        #if request.form.get('datmtme') >= datetime.now():
        if 'photo' in request.files:      
            photo = request.files['photo']
            if photo:
                extension = photo.filename.split('.')
                #print "changing photo"
                #Needs to be revised
                path_to_photo = './static/images/events_photos/' + secure_filename(str(request.form.get('id')) + '.' + extension[-1])
                photo.save(path_to_photo)
            else:
                #print "not changing photo"
                path_to_photo = originEvent.photo
                
        #print path_to_photo    
        event = Event(
            id = request.form.get('id'),
            name = request.form.get('name'),
            description = request.form.get('description'),
            price = request.form.get('price'),
            address = request.form.get('address'),
            date_time_close = request.form.get('datmtme'),
            accessories_purchased = request.form.get('accessories'),
            photo = path_to_photo
            )
        event.modify()
        flash('You successfully modified Event!')
    #flash('Event cannot be completed before it starts')
    return redirect (url_for('showevent', id=originid))
@app.route('/deactevent', methods=['GET', 'POST'])
@login_required
def deactivate_event():
    if request.method == 'POST':
        event = Event(
            id = request.form.get('id'),
            active = 0)
        event.deactivate()
        flash('You successfully deactivated Event!')
    return render_template('profile.html', user = User.get_by_username(session['username']))

@app.route('/events', methods=['GET', 'POST'])
@login_required
def allevents():
    if request.method == 'POST':
        filter_by_name = request.form.get('srch')
        if filter_by_name != '':
            return render_template('events.html', username = session['username'], events = Event.get_by_name(filter_by_name)[::-1])
        else:
            return render_template('events.html', username = session['username'], events = Event.get_all()[::-1])
    return render_template('events.html', username = session['username'], events = Event.get_all()[::-1])

def confirmation_mail(msg_for_what, rm , client, event_obj, eventid):
    if msg_for_what == 'repairman':
        chosen_repariman_msg = "\r\n".join([
            "From: tygayoinc@gmail.com",
            "To: " + rm.email,
            "Subject: Chosen to " + event_obj.name,
            "",
            "Dear " + rm.name + ",",
            "",
            "This mail is from Tygayo Inc. You have been chosen to take care of " + event_obj.name + ".",
            "The event takes place at " + event_obj.address + ", scheduled for " + str(event_obj.date_time_create) + ".",
            "",
            "The event details are in the link bellow:",
            "http://localhost:5000" + url_for('showevent', id=eventid),
            "",
            "Best Regards,",
            "TygAyo Inc."
            ])
        return chosen_repariman_msg

    if msg_for_what == 'client':
        msg_to_client = "\r\n".join([
                "From: tygayoinc@gmail.com",
                "To: " +  client.email,
                "Subject: Chose repairman for " + event_obj.name,
                "",
                "Dear " + client.name + ",",
                "",
                "This mail is from Tygayo Inc. You choose " + rm.name + " for repairman.",
                "The event takes place at " + event_obj.address + ", scheduled for " + str(event_obj.date_time_create) + ".",
                "",
                "The event details are in the link bellow:",
                "http://localhost:5000" + url_for('showevent', id=eventid),
                "",
                "Best Regards,",
                "TygAyo Inc."
                ])
        return msg_to_client
        
def registration_mail(user):
        user_msg = "\r\n".join([
            "From: tygayoinc@gmail.com",
            "To: " + user.email,
            "Subject: Tygayo inc - Registration",
            "",
            "Dear " + user.name + ",",
            "",
            "You have sacessfully registered on portal Tygayo Inc. Thank You for Your interest."
            "",
            "Best Regards,",
            "TygAyo Inc."
            "http://localhost:5000"
            ])
        return user_msg  