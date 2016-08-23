# -*- coding: utf-8 -*-

from functools import wraps
from flask import request, render_template, Response, g, session, redirect, url_for, flash, send_from_directory, Blueprint
from app import app, db, babel
from datetime import datetime
from model import User, Event, Applied_repairman  # from database
from werkzeug import secure_filename
from sqlalchemy.sql import and_, select, or_
from smtplib import SMTP
from flask.ext.babel import gettext, ngettext, gettext, refresh



@babel.localeselector
def get_locale():
    if g.lang_code:
        return g.lang_code
    return 'hr'  # deafult languages

@app.route('/')
def index_app():
    return redirect("/hr/")

bp = Blueprint('frontend', __name__, url_prefix='/<lang_code>')

@bp.url_defaults
def add_language_code(endpoint, values):
    values.setdefault('lang_code', g.lang_code)


@bp.url_value_preprocessor
def pull_lang_code(endpoint, values):
    g.lang_code = values.pop('lang_code')

def login_required(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        if not ('id' in session):
            refresh()
            flash(gettext('You need to signin!'))
            return redirect('/signin')
        return fn(*args, **kwargs)
    return decorated_view

@bp.route('/')
def index():
    events = Event.get_all()[:-10:-1]
    for event in events:
        if event.photo == None:
            event.photo = "../static/images/events_photos/default.jpg"
    return render_template('index.html', events = events)

@bp.route('/about')
def about():
    return render_template('about.html',username = session.get('username'))

@bp.route('/startup')
@login_required
def startup():
    events = Event.get_all()[:-10:-1]
    for event in events:
        if event.photo == None:
            event.photo = "../static/images/events_photos/default.jpg"
    return render_template('startup.html', username = session['username'], events = events)

@bp.route('/signin', methods=['GET', 'POST'])
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
            refresh()
            flash(gettext('You entered wrong data!'))
            return redirect(url_for('.login'))
        refresh()
        flash(gettext('Hello ' + user.name + ' ' + user.surename + '!'))
        return redirect (url_for('.startup'))
    else:
        return redirect (url_for('.index'))

@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        path_to_photo = None
        #if request.form.get('datmtme') >= datetime.now():
        usernamecheck = User.get_by_username(request.form.get('username'))
        mailcheck = User.get_by_mail(request.form.get('email'))
        if mailcheck != None:
            refresh()
            flash(gettext('We are sorry, register was not successful as this email adress is already registered.'))
            return redirect (url_for('.index'))
        elif usernamecheck != None:
            refresh()
            flash(gettext('We are sorry, register was not successful as this username is already registered.'))
            return redirect (url_for('.index'))
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
            print "Evo smo: ",request.files
            print "Tak sto sad: ",request.files.getlist('photo')
            # pho = request.files[0]
            # print pho.filename
            if 'photo' in request.files and request.files['photo'].filename != '':
                photo = request.files['photo']
                extension = photo.filename.split('.')
                path_to_photo = '.\\static\\images\\users_avatar\\' + secure_filename(str(us.id) + '.' + extension[-1])
                photo.save(path_to_photo)
                us.picture = path_to_photo
                us.save()
            refresh()
            flash(gettext('You have successfully Registered!'))
            session['id'] = us.id
            session['username'] = us.username
            fromaddr = "%s <%s>" % ('TygAyo','tygayoinc@gmail.com')
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
            return redirect (url_for('.startup'))
    else:
        return redirect (url_for('.index'))

@app.route('/signout')
def logout():
    session.pop('username', None)
    session.pop('id', None)
    return redirect('/')

#@app.route('/startup')
#@login_required
#def start():
#    return render_template('startup.html')
    
@bp.route('/edetails/<id>')
def showevent(id):
    event = db.session.query(Event).get(id)
    if not event:
        abort(404)
    user = db.session.query(User).get(event.user_id)
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
        if event.repairman_id:
            repairman = User.get(event.repairman_id)
        else:
            repairman = None
        
    else:    
        # Check If the user is already signed up for this event
        repairman = None
        s = select([(Applied_repairman.id)]).where(
                                        and_(
                                            Applied_repairman.event_id == event.id,
                                            Applied_repairman.repairman_id == cuserId)
                                        )
        result = db.engine.execute(s).fetchall()
        if len(result) != 0:
            already = 1
            # print "The user is signed up in this events:"
    if event.photo == None:
        event.photo = "./static/images/events_photos/default.jpg"
    
    return render_template('edetails.html',username = session.get('username'),event=event,
                                                                            user=user,
                                                                   users = Signedupusers,
                                                                   already = already,
                                                                   cuserId = cuserId,
                                                                   accessP = accessP,
                                                                   repairman = repairman)

                                                                   
@app.route('/signup', methods=['POST','GET'])
def signup():
    eventid = request.form.get('event_to_signup')
    if request.method == 'POST':      
        signed = Applied_repairman(
            event_id = eventid,
            repairman_id = session.get('id')
            )
        signed.save()
        refresh()
        flash(gettext('You have successfully signed up for the event!'))
        id = session.get('id')
        user = User.get(id)    
    return redirect (url_for('.myPage',username=user.username))
    
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
        refresh()
        flash(gettext('You have successfully chosed a repairman!'))
    return redirect (url_for('.showevent', id=eventid))
    
@bp.route('/createvent', methods=['GET', 'POST'])
@login_required
def create_an_event():
    if request.method == 'POST':
        path_to_photo = None
        #if request.form.get('datmtme') >= datetime.now():
        if 'photo' in request.files and request.files['photo'].filename != '':
            photo = request.files['photo']
            print "Ovo je foto:", photo
            extension = photo.filename.split('.')
            path_to_photo = '.\\static\\images\\events_photos\\' + secure_filename(str(session['id']) + '.' + extension[-1])
            photo.save(path_to_photo)

        event = Event(
            name = request.form.get('name'),
            description = request.form.get('description'),
            price = request.form.get('price'),
            address = request.form.get('address'),
            date_time_create = datetime.now(),
            date_time_execute = datetime.strptime(request.form.get('datmtme'), "%m/%d/%Y %I:%M %p"),
            accessories_purchased = request.form.get('accessories'),
            user_id = session.get('id'),
            active = 1,
            closed = 0,
            photo = path_to_photo)
            
        if (datetime.strptime(request.form.get('datmtme'), "%m/%d/%Y %I:%M %p") > datetime.now()):    
            event.save()
            refresh()
            flash(gettext('You have successfully created Event!'))
        else:
            refresh()
            flash(gettext("Execution Date of Event can't be before Event is created!", "warning"))
    #flash('Event cannot be completed before it starts')
    return redirect (url_for('.myPage', username = session['username']))

@bp.route('/profile/<username>')
def profilePage(username):
    if len(username) != 0 and User.get_by_username(username) != None:
        user = User.get_by_username(username)
        #user_photo = user.picture
        if user.picture != None:
            return render_template('profile.html', user = user, cuserId = session.get('id'))
        else:
            user.picture = "./static/images/users_avatar/default.jpg"
            return render_template('profile.html', user = user, cuserId = session.get('id'))
    else:
        refresh()
        flash(gettext("%s doesn't exist!" %username, "warning"))
        return redirect (url_for('.profilePage', username = session['username']))

@bp.route('/mypage/<username>')
@bp.route('/mypage/')
@login_required
def myPage(username):
    if len(username) != 0 and User.get_by_username(username) != None:
        user = User.get_by_username(username)
        sqltxt = select([(Applied_repairman.event_id)]).where(Applied_repairman.repairman_id == user.id)
        allsignedup = db.engine.execute(sqltxt).fetchall()
        allsignedups = [r[0] for r in allsignedup]
        # Fetch Event objects for these ids
        sqltxt2 = select([(Event)]).where(
                                          or_(Event.repairman_id == user.id,
                                              and_(
                                                   Event.id.in_(allsignedups),
                                                   Event.repairman_id == None                                  
                                              )
                                          
                                          ))
        Signedupuevents = db.engine.execute(sqltxt2).fetchall()

        #Get all events creted by User
        event_created_by_user_query = select([Event]).where(Event.user_id == user.id)
        event_created_by_user = db.engine.execute(event_created_by_user_query).fetchall()
        return render_template('mypage.html', user = user, CreatedEvents = event_created_by_user, SUPevents = Signedupuevents)
    else:
        refresh()
        flash(gettext("You are not %s!" %username, "warning"))
        return redirect (url_for('.myPage', username = session['username']))

@bp.route('/modifyuser', methods=['GET', 'POST'])
@login_required
def modify_an_user():
    if request.method == 'POST':
        path_to_photo = None
        user_n = User.get_by_username(session['username'])
        #if request.form.get('datmtme') >= datetime.now():
        if 'photo' in request.files and request.files['photo'].filename != '':
            photo = request.files['photo']
            if photo:
                extension = photo.filename.split('.')
                #Needs to be revised
                path_to_photo = './static/images/users_avatar/' + secure_filename(str(session['id']) + '.' + extension[-1])
                photo.save(path_to_photo)
            else:
                path_to_photo = user_n.picture

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
        refresh()
        flash(gettext('You successfully modified Profile!'))
    #flash('Event cannot be completed before it starts')
    return redirect (url_for('.profilePage', username = session['username']))

@app.route('/modifyevent', methods=['GET', 'POST'])
@login_required
def modify_an_event():
    if request.method == 'POST':
        path_to_photo = None
        user_n = User.get_by_username(session['username'])
        originid = request.form.get('id')
        originEvent = Event.get(originid)
        #if request.form.get('datmtme') >= datetime.now():
        if 'photo' in request.files and request.files['photo'].filename != '':      
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
        print originEvent.date_time_create
        print request.form.get('datmtme')
        event = Event(
            id = request.form.get('id'),
            name = request.form.get('name'),
            description = request.form.get('description'),
            price = request.form.get('price'),
            address = request.form.get('address'),
            date_time_execute = datetime.strptime(request.form.get('datmtme'), "%m/%d/%Y %I:%M %p"),
            accessories_purchased = request.form.get('accessories'),
            photo = path_to_photo
            )
        if (datetime.strptime(request.form.get('datmtme'), "%m/%d/%Y %I:%M %p") > datetime.now()):
            event.modify()
            refresh()
            flash(gettext('You successfully modified Event!'))
        else:
            refresh()
            flash(gettext("Execution Date of Event can't be before Event is created!", "warning"))
    #flash('Event cannot be completed before it starts')
    return redirect (url_for('.showevent', id=originid))
    
@app.route('/deactevent', methods=['GET', 'POST'])
@login_required
def deactivate_event():
    if request.method == 'POST':
        event = Event(
            id = request.form.get('id'),
            active = 0)
        event.deactivate()
        refresh()
        flash(gettext('You successfully deactivated Event!'))
    return redirect (url_for('.showevent', id=request.form.get('id')))


@app.route('/unassign', methods=['GET', 'POST'])
@login_required
def un_assign():
    if request.method == 'POST':        
        link = Applied_repairman.get_link(request.form.get('id'),session['id'])
        print link.id
        link.delete()
        refresh()      
        flash(gettext('You have successfully un-asigned from the Event!'))
    return redirect (url_for('.showevent', id=request.form.get('id')))
        
@app.route('/declineevent', methods=['GET', 'POST'])
@login_required
def decline_event():
    if request.method == 'POST':
        event = Event.get(request.form.get('id'))
        print datetime.now()
        print event.date_time_execute
        if datetime.now() < event.date_time_execute:
            event.activate()
          # potential problem with different time zones
        event.remove_repairman()
        event.decline()
        
        link = Applied_repairman.get_link(request.form.get('id'),session['id'])
        print link.id
        link.delete()  
        refresh()          
        flash(gettext('You have successfully declined the Event!'))
    return redirect (url_for('.showevent', id=request.form.get('id')))
    
@app.route('/closeevent', methods=['GET', 'POST'])
@login_required
def close_event():
    if request.method == 'POST':
        eventid = request.form.get('id')
        event = Event(
            id = eventid,
            active = 0,
            closed = 1)
        event.close()
        print 'event was closed'
        refresh()
        flash(gettext('Event has been Finished!'))
    return redirect (url_for('.showevent', id=eventid))

@bp.route('/events', methods=['GET', 'POST'])
def allevents():
    events = Event.get_all()[::-1]
    for event in events:
        if event.photo == None:
            event.photo = "../static/images/events_photos/default.jpg"

    if request.method == 'POST':
        filter_by_name = request.form.get('srch')
        if filter_by_name != '':
            events_by_name = Event.get_by_name_or_description(filter_by_name)[::-1]
            for evnt in events_by_name:
                if evnt.photo == None:
                    evnt.photo = "../static/images/events_photos/default.jpg"
            if  events_by_name != None:       
                return render_template('events.html', username = session.get('username'), events = events_by_name, srch_value=filter_by_name)
            else:
                return render_template('events.html', username = session.get('username'), events = None, srch_value=filter_by_name)
        #else:
        #    return render_template('events.html', username = session.get('username'), events = Event.get_all()[::-1])
    return render_template('events.html', username = session.get('username'), events = events)

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
            "http://tygayo.herokuapp.com/" + url_for('.showevent', id=eventid),
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
                "http://tygayo.herokuapp.com/" + url_for('.showevent', id=eventid),
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
            "http://tygayo.herokuapp.com/"
            ])
        return user_msg  

app.register_blueprint(bp)