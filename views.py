# -*- coding: utf-8 -*-

from functools import wraps
from flask import request, render_template, Response, g, session, redirect, url_for, flash, send_from_directory, \
    Blueprint
from app import app, db, babel
from datetime import datetime
from model import User, Event, Applied_repairman, Event_comment, Tag, Repairman_comment  # from database
from werkzeug import secure_filename
from sqlalchemy.sql import and_, select, or_, func
from smtplib import SMTP
from flask.ext.babel import gettext, ngettext, refresh
from flask.ext.sqlalchemy import BaseQuery
import os
from operator import itemgetter, attrgetter


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
            return redirect(url_for('.login'))
        return fn(*args, **kwargs)

    return decorated_view


@bp.route('/')
def index():
    total_users = len(User.get_all())
    if not total_users:
        total_users = 0
    active_events = Event.get_active_events().count()
    if not active_events:
        active_events = 0
    closed_events = Event.get_closed_events().count()
    if not closed_events:
        closed_events = 0
    money_earned = db.session.query(func.sum(Event.price)).filter(Event.closed == bool(1)).scalar()
    if not money_earned:
        money_earned = 0
    events = Event.get_all()[0][:-10:-1]
    for event in events:
        if event.photo == None:
            event.photo = "../static/images/events_photos/default.jpg"
    return render_template('index.html', events=events, active_events=active_events, closed_events=closed_events,
                           total_users=total_users, money_earned=int(money_earned))


@bp.route('/about')
def about():
    active_events = Event.get_active_events().count()
    return render_template('about.html', username=session.get('username'), active_events=active_events)


@bp.route('/modalCreateEvent')
def modalCreateEvent():
    return render_template('modalCreateEvent.html')

@bp.route('/modalModifyEvent')
def modalModifyEvent():
    print "boj bok"
    eventid = request.args.get('eventId')
    event = db.session.query(Event).get(eventid)
    return render_template('modalModifyEvent.html',event=event)

@bp.route('/startup')
@login_required
def startup():
    total_users = len(User.get_all())
    active_events = Event.get_active_events().count()
    closed_events = Event.get_closed_events().count()
    money_earned = db.session.query(func.sum(Event.price)).filter(Event.closed == bool(1)).scalar()
    events = Event.get_all()[0][:-10:-1]
    for event in events:
        if event.photo == None:
            event.photo = "../static/images/events_photos/default.jpg"
    return render_template('startup.html', username=session['username'], events=events, active_events=active_events,
                           closed_events=closed_events, total_users=total_users, money_earned=money_earned)


@bp.route('/signin', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # username = request.form.get('username')
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
        return redirect(url_for('.startup'))
    else:
        return redirect(url_for('.index'))


@bp.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        path_to_photo = None
        # if request.form.get('datmtme') >= datetime.now():
        usernamecheck = User.get_by_username(request.form.get('username'))
        mailcheck = User.get_by_mail(request.form.get('email'))
        if mailcheck != None:
            refresh()
            flash(gettext('We are sorry, register was not successful as this email adress is already registered.'))
            return redirect(url_for('.index'))
        elif usernamecheck != None:
            refresh()
            flash(gettext('We are sorry, register was not successful as this username is already registered.'))
            return redirect(url_for('.index'))
        else:
            user = User(
                name=request.form.get('name'),
                surename=request.form.get('surename'),
                username=request.form.get('username'),
                address=request.form.get('address'),
                email=request.form.get('email'),
                password=request.form.get('password'),
                mobile=request.form.get('mobile'),
                joindate=datetime.now())
            user.save()

            us = User.get_by_username(user.username)
            print "Tohle je files"
            print "Evo smo: ", request.files
            print "Tak sto sad: ", request.files.getlist('photo')
            # pho = request.files[0]
            # print pho.filename
            if request.files['photo'].filename != '':
                photo = request.files['photo']
                extension = photo.filename.split('.')
                path_to_photo = './static/images/users_avatar/' + secure_filename(str(us.id) + '.' + extension[-1])
                # photo.save(path_to_photo)
                us.picture = path_to_photo
                us.save()
            refresh()
            flash(gettext('You have successfully Registered!'))
            session['id'] = us.id
            session['username'] = us.username

            fromaddr = "%s <%s>" % ('TygAyo', 'registration@tygayo.herokuapp.com')
            toaddrs = us.email
            msg = registration_mail(us)
            username = '953dfa2af4a2c579a134d7aaa74c646b'
            password = '91626ab7ed85ca7162602bb37331e32a'
            server = SMTP("in-v3.mailjet.com", 587)
            server.ehlo()
            # server.starttls()
            server.login(username, password)
            server.sendmail(fromaddr, toaddrs, msg)
            server.close()

            return redirect(url_for('.startup'))
    else:
        return redirect(url_for('.index'))


@app.route('/signout')
def logout():
    session.pop('username', None)
    session.pop('id', None)
    return redirect('/')


# @app.route('/startup')
# @login_required
# def start():
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
    cuserId = session.get('id')
    Signedupusers = None
    already = 0
    # Check for event comments
    sComs = select([(Event_comment)]).where(
        Event_comment.event_id == event.id)
    eventcomments = db.engine.execute(sComs).fetchall()

    comms_list = [str(x[2]) for x in eventcomments]
    author_ids = [str(x[3]) for x in eventcomments]
    date_list = [str(x[4]) for x in eventcomments]

    uComs = select([(User)]).where(User.id.in_(author_ids))
    usercomments = db.engine.execute(uComs).fetchall()
    # this is done because we do not know how to iterate and object in jQuery
    # in jQuery we would need to use someting like objects[i].comment
    # so we send list of stings instead

    user_list = [str(x[3]) for x in usercomments]
    userid_list = [str(x[0]) for x in usercomments]
    user_dict = dict(zip(userid_list, user_list))
    author_list = [];

    for y in author_ids:
        author_list.append(user_dict[str(y)])
    # Checking if the user is owner of this event
    if event.user_id == cuserId:
        # If yes, fetch ids of all signedup users for this event
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
    active_events = Event.get_active_events().count()
    return render_template('edetails.html', username=session.get('username'), event=event,
                           user=user,
                           users=Signedupusers,
                           already=already,
                           cuserId=cuserId,
                           accessP=accessP,
                           repairman=repairman,
                           eventcomments=comms_list,
                           author_list=author_list,
                           date_list=date_list,
                           active_events=active_events
                           )


@bp.route('/signup', methods=['POST', 'GET'])
def signup():
    eventid = request.form.get('event_to_signup')
    if request.method == 'POST':
        signed = Applied_repairman(
            event_id=eventid,
            repairman_id=session.get('id')
        )
        signed.save()
        refresh()
        flash(gettext('You have successfully signed up for the event!'))
        id = session.get('id')
        user = User.get(id)
    return redirect(url_for('.myPage', username=user.username))


@bp.route('/chooserm', methods=['POST'])
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

        toaddrs = rm.email
        toaddrs_client = client.email
        msg = confirmation_mail('repairman', rm, client, event, eventid)
        msg_client = confirmation_mail('client', rm, client, event, eventid)

        fromaddr = "%s <%s>" % ('TygAyo', 'eventrepairman@tygayo.herokuapp.com')
        username = '953dfa2af4a2c579a134d7aaa74c646b'
        password = '91626ab7ed85ca7162602bb37331e32a'
        server = SMTP("in-v3.mailjet.com", 587)
        server.ehlo()
        # server.starttls()
        server.login(username, password)
        server.sendmail(fromaddr, toaddrs, msg)
        server.sendmail(fromaddr, toaddrs_client, msg_client)
        server.close()
        refresh()
        flash(gettext('You have successfully chosed a repairman!'))
    return redirect(url_for('.showevent', id=eventid))


@bp.route('/createvent', methods=['GET', 'POST'])
@login_required
def create_an_event():
    if request.method == 'POST':
        path_to_photo = None
        # if request.form.get('datmtme') >= datetime.now():
        if 'photo' in request.files and request.files['photo'].filename != '':
            photo = request.files['photo']
            extension = photo.filename.split('.')
            path_to_photo = './static/images/events_photos/' + secure_filename(str(session['id']) + '.' + extension[-1])
            photo.save(path_to_photo)

        if request.form.get('cityList') == "Zagreb":
            neighborhoodinput = request.form.get('neighborhoodList')
        else:
            neighborhoodinput = ""
        default_tags = request.form.get('tag-default').strip().split(',')
        tags = default_tags + request.form.get('tag').split(',')
        event = Event(
            name=request.form.get('name'),
            description=request.form.get('description'),
            price=request.form.get('price'),
            city=request.form.get('cityList'),
            neighborhood=neighborhoodinput,
            address=request.form.get('address'),
            date_time_create=datetime.now(),
            date_time_execute=datetime.strptime(request.form.get('datmtme'), "%m/%d/%Y %I:%M %p"),
            accessories_purchased=request.form.get('accessories'),
            user_id=session.get('id'),
            active=1,
            closed=0,
            photo=path_to_photo)
        if (datetime.strptime(request.form.get('datmtme'), "%m/%d/%Y %I:%M %p") > datetime.now()):
            event.save()
            refresh()
            flash(gettext('You have successfully created Event!'))
        else:
            refresh()
            flash(gettext("Execution Date of Event can't be before Event is created!"), "warning")
        for tg in tags:
            tag = Tag(
                event_id=event.id,
                tag_description=tg
            )
            tag.save()
    # flash('Event cannot be completed before it starts')
    return redirect(url_for('.myPage', username=session['username']))


@bp.route('/addcomment', methods=['GET', 'POST'])
@login_required
def add_comment():
    if request.method == 'POST':
        eventcomment = Event_comment(
            event_id=request.form.get('event_id'),
            comment=request.form.get('commenttext'),
            user_id=request.form.get('user_id'),
            date_time_post=datetime.now()
        )
        eventcomment.save()
        # flash('Event cannot be completed before it starts')
    return redirect(url_for('.showevent', id=request.form.get('event_id')))


@bp.route('/profile/<username>')
def profilePage(username):
    active_events = Event.get_active_events().count()
    if len(username) != 0 and User.get_by_username(username) != None:
        user = User.get_by_username(username)
        xps = lookuptable_level_xp.keys()
        xps.sort()
        next_level_xp = 0
        for xp in xps:
            if user.xp < xp:
                next_level_xp = xp
                break
        bg_color = ()
        if user.level < 6:
            bg_color = lookup_color_levels[1]
        elif user.level < 11:
            bg_color = lookup_color_levels[2]
        elif user.level < 16:
            bg_color = lookup_color_levels[3]
        else:
            bg_color = lookup_color_levels[4]
        # Check for user comments
        commentsquery = select([(Repairman_comment)]).where(
            and_(
                Repairman_comment.repairman_id == user.id,
                Repairman_comment.comment != ""))

        repairmancomments = db.engine.execute(commentsquery).fetchall()

        comms_list = [str(x[1]) for x in repairmancomments]
        author_ids = [str(x[3]) for x in repairmancomments]
        event_ids = [str(x[4]) for x in repairmancomments]
        date_list = [str(x[5]) for x in repairmancomments]

        authorQuery = select([(User)]).where(User.id.in_(author_ids))
        authors = db.engine.execute(authorQuery).fetchall()
        # this is done because we do not know how to iterate and object in jQuery
        # in jQuery we would need to use someting like objects[i].comment
        # so we send list of stings instead, 


        user_list = [str(x[3]) for x in authors]
        userid_list = [str(x[0]) for x in authors]
        user_dict = dict(zip(userid_list, user_list))

        author_list = []
        for y in author_ids:
            author_list.append(user_dict[str(y)])
        
        # user_photo = user.picture
        if user.picture != None:
            return render_template('profile.html', user=user, cuserId=session.get('id'), active_events=active_events,
                                        usercomments=comms_list,
                                        author_list=author_list,
                                        event_list=event_ids,
                                        date_list=date_list,
                                        next_level_xp=next_level_xp,
                                        bg_color=bg_color)
        else:
            user.picture = "./static/images/users_avatar/default.jpg"
            return render_template('profile.html', user=user, cuserId=session.get('id'), active_events=active_events,
                                        usercomments=comms_list,
                                        author_list=author_list,
                                        event_list=event_ids,
                                        date_list=date_list,
                                        next_level_xp=next_level_xp,
                                        bg_color=bg_color)
    else:
        refresh()
        print "Refreshing"
        flash(gettext("%s doesn't exist!") % username, "warning")
        return redirect(url_for('.profilePage', username=session['username']))


@bp.route('/mypage/<username>')
@bp.route('/mypage/')
@login_required
def myPage(username):
    active_events = Event.get_active_events().count()
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

        # Get all events creted by User
        event_created_by_user_query = select([Event]).where(Event.user_id == user.id)
        event_created_by_user = db.engine.execute(event_created_by_user_query).fetchall()
        return render_template('mypage.html', user=user, CreatedEvents=event_created_by_user, SUPevents=Signedupuevents,
                               active_events=active_events)
    else:
        refresh()
        flash(gettext("You are not %s!") % username, "warning")
        return redirect(url_for('.myPage', username=session['username']))


@bp.route('/modifyuser', methods=['GET', 'POST'])
@login_required
def modify_an_user():
    if request.method == 'POST':
        path_to_photo = None
        user_n = User.get_by_username(session['username'])
        # if request.form.get('datmtme') >= datetime.now():
        if 'photo' in request.files and request.files['photo'].filename != '':
            photo = request.files['photo']
            if photo:
                extension = photo.filename.split('.')
                # Needs to be revised
                path_to_photo = './static/images/users_avatar/' + secure_filename(
                    str(session['id']) + '.' + extension[-1])
                photo.save(path_to_photo)
            else:
                path_to_photo = user_n.picture

        user = User(
            id=session['id'],
            name=request.form.get('name'),
            surename=request.form.get('surname'),
            username=request.form.get('username'),
            address=request.form.get('address'),
            email=request.form.get('email'),
            mobile=request.form.get('mobile'),
            picture=path_to_photo)
        user.modify()
        refresh()
        flash(gettext('You successfully modified Profile!'))
    # flash('Event cannot be completed before it starts')
    return redirect(url_for('.profilePage', username=session['username']))


@bp.route('/modifyevent', methods=['GET', 'POST'])
@login_required
def modify_an_event():
    if request.method == 'POST':
        path_to_photo = None
        originid = request.form.get('id')
        originEvent = Event.get(originid)
        # if request.form.get('datmtme') >= datetime.now():
        if 'photo' in request.files and request.files['photo'].filename != '':
            photo = request.files['photo']
            if photo:
                extension = photo.filename.split('.')
                # print "changing photo"
                # Needs to be revised
                path_to_photo = './static/images/events_photos/' + secure_filename(
                    str(request.form.get('id')) + '.' + extension[-1])
                photo.save(path_to_photo)
            else:
                # print "not changing photo"
                path_to_photo = originEvent.photo

        # print path_to_photo
        print originEvent.date_time_create
        print request.form.get('datmtme')

        if request.form.get('cityList') == "Zagreb":
            neighborhoodinput = request.form.get('neighborhoodList')
        else:
            neighborhoodinput = ""
        event = Event(
            id=request.form.get('id'),
            name=request.form.get('name'),
            description=request.form.get('description'),
            price=request.form.get('price'),
            city=request.form.get('cityList'),
            neighborhood=neighborhoodinput,
            address=request.form.get('address'),
            date_time_execute=datetime.strptime(request.form.get('datmtme'), "%m/%d/%Y %I:%M %p"),
            accessories_purchased=request.form.get('accessories'),
            photo=path_to_photo
        )
        if (datetime.strptime(request.form.get('datmtme'), "%m/%d/%Y %I:%M %p") > datetime.now()):
            event.modify()
            refresh()
            send_mail_notification_about_changed_event(originid)
            flash(gettext('You successfully modified Event!'))
        else:
            refresh()
            flash(gettext("Execution Date of Event can't be before Event is created!"), "warning")
    # flash('Event cannot be completed before it starts')
    return redirect(url_for('.showevent', id=originid))


@bp.route('/deactevent', methods=['GET', 'POST'])
@login_required
def deactivate_event():
    if request.method == 'POST':
        event = Event(
            id=request.form.get('id'),
            active=0)
        event.deactivate()
        refresh()
        flash(gettext('You successfully deactivated Event!'))
    return redirect(url_for('.showevent', id=request.form.get('id')))


@bp.route('/unassign', methods=['GET', 'POST'])
@login_required
def un_assign():
    if request.method == 'POST':
        link = Applied_repairman.get_link(request.form.get('id'), session['id'])
        print link.id
        link.delete()
        refresh()
        flash(gettext('You have successfully un-asigned from the Event!'))
    return redirect(url_for('.showevent', id=request.form.get('id')))


@bp.route('/declineevent', methods=['GET', 'POST'])
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

        link = Applied_repairman.get_link(request.form.get('id'), session['id'])
        print link.id
        link.delete()
        refresh()
        flash(gettext('You have successfully declined the Event!'))
    return redirect(url_for('.showevent', id=request.form.get('id')))


@bp.route('/closeevent', methods=['GET', 'POST'])
@login_required
def close_rate_event():
    if request.method == 'POST':
        eventid = request.form.get('eventid')
        rate_it = request.form.get('rating-id')
        repairman_comment = Repairman_comment(
            comment =  request.form.get('commenttext'),
            repairman_id = request.form.get('repairmanid'),
            client_id = request.form.get('clientid'),
            event_id = eventid,
            date_time_post = datetime.now())
        repairman_comment.save()
        event = Event(
            id=eventid,
            active=0,
            closed=1,
            rate=rate_it)
        event.close_rate()
        refresh()
        calculate_repairman_average_rate(Event.get(eventid).repairman_id)
        calculate_xp(rate_it, Event.get(eventid).price, Event.get(eventid).repairman_id)
        flash(gettext('Event has been Finished!'))
    return redirect(url_for('.showevent', id=eventid))


@bp.route('/events', methods=['GET', 'POST'])
@bp.route('/events/<int:page>', methods=['GET', 'POST'])
def allevents(page=1):
    active_events = Event.get_active_events().count()
    events, pages = Event.get_all(page)
    for event in events:
        if event.photo == None:
            event.photo = "../static/images/events_photos/default.jpg"

    if request.method == 'POST':
        default_tags = request.form.get('tag-default').strip()
        if default_tags != None:
            filter_by_name = request.form.get('srch') + default_tags
        else:
            filter_by_name = request.form.get('srch')
        if filter_by_name != '':
            events_by_name, pages = Event.get_by_name_tag_or_description(filter_by_name, page)
            for evnt in events_by_name:
                if evnt.photo == None:
                    evnt.photo = "../static/images/events_photos/default.jpg"
            if events_by_name != None:
                return render_template('events.html', username=session.get('username'), events=events_by_name,
                                       srch_value=filter_by_name, pages=pages, active_events=active_events)
            else:
                return render_template('events.html', username=session.get('username'), events=None,
                                       srch_value=filter_by_name, active_events=active_events)
                # else:
                #    return render_template('events.html', username = session.get('username'), events = Event.get_all()[::-1])
    return render_template('events.html', username=session.get('username'), events=events, pages=pages,
                           active_events=active_events)


@bp.route('/rank')
@bp.route('/rank/username')
def rank_page(username=None):
    active_events = Event.get_active_events().count()
    repairmen = User.get_all_xp_desc()
    return render_template('rank.html', repairmen = repairmen, username=session.get('username'), active_events=active_events)


def confirmation_mail(msg_for_what, rm, client, event_obj, eventid):
    if msg_for_what == 'repairman':
        chosen_repariman_msg = "\r\n".join([
            "From: eventrepairman@tygayo.herokuapp.com",
            "To: " + rm.email,
            "Subject: Chosen to " + event_obj.name,
            "",
            "Dear " + rm.name + ",",
            "",
            "This mail is from Tygayo Inc. You have been chosen to take care of " + event_obj.name + ".",
            "The event takes place at " + event_obj.address + ", scheduled for " + str(
                event_obj.date_time_create) + ".",
            "",
            "The event details are in the link bellow:",
            "http://tygayo.herokuapp.com" + url_for('.showevent', id=eventid),
            "",
            "Best Regards,",
            "TygAyo Inc."
        ])
        return chosen_repariman_msg

    if msg_for_what == 'client':
        msg_to_client = "\r\n".join([
            "From: eventrepairman@tygayo.herokuapp.com",
            "To: " + client.email,
            "Subject: Chose repairman for " + event_obj.name,
            "",
            "Dear " + client.name + ",",
            "",
            "This mail is from Tygayo Inc. You choose " + rm.name + " for repairman.",
            "The event takes place at " + event_obj.address + ", scheduled for " + str(
                event_obj.date_time_create) + ".",
            "",
            "The event details are in the link bellow:",
            "http://tygayo.herokuapp.com" + url_for('.showevent', id=eventid),
            "",
            "Best Regards,",
            "TygAyo Inc."
        ])
        return msg_to_client


def registration_mail(user):
    user_msg = "\r\n".join([
        "From: registration@tygayo.herokuapp.com",
        "To: " + user.email,
        "Subject: Tygayo inc - Registration",
        "",
        "Dear " + user.name + ",",
        "",
        "You have successfully registered on portal Tygayo Inc. Thank You for Your interest."
        "",
        "Best Regards,",
        "TygAyo Inc."
        "http://tygayo.herokuapp.com/"
    ])
    return user_msg


def notification_mail_about_changed_event(signedupusers, evnt_id):
    modify_msg = {}
    for repairman in signedupusers:
        modify_msg[repairman.id] = "\r\n".join([
            "From: eventrepairman@tygayo.herokuapp.com",
            "To: " + repairman.email,
            "Subject: Tygayo inc - '" + Event.get(evnt_id).name + "' event modified",
            "",
            "Dear " + repairman.name + ",",
            "",
            "Details of event '" + Event.get(evnt_id).name + "' you signed up for have changed",
            "",
            "The event details are in the link bellow:",
            "http://tygayo.herokuapp.com" + url_for('.showevent', id=evnt_id),
            "",
            "Best Regards,",
            "TygAyo Inc.",
            "http://tygayo.herokuapp.com/"
        ])
    return modify_msg


def send_mail_notification_about_changed_event(evnt_id):
    id_list_of_signedup_repairmen_query = select([(Applied_repairman.repairman_id)]).where(
        Applied_repairman.event_id == evnt_id)
    allsignedup = db.engine.execute(id_list_of_signedup_repairmen_query).fetchall()
    allsignedups = [r[0] for r in allsignedup]
    # Fetch User objects for these ids
    list_of_signedup_repairmen_object = select([User]).where(User.id.in_(allsignedups))
    Signedupusers = db.engine.execute(list_of_signedup_repairmen_object).fetchall()
    map_of_msg_for_repairmen = notification_mail_about_changed_event(Signedupusers, evnt_id)
    username = '953dfa2af4a2c579a134d7aaa74c646b'
    password = '91626ab7ed85ca7162602bb37331e32a'
    server = SMTP("in-v3.mailjet.com", 587)
    server.ehlo()
    server.login(username, password)
    fromaddr = "%s <%s>" % ('TygAyo', 'eventrepairman@tygayo.herokuapp.com')
    for repairman, repairman_msg in zip(Signedupusers, map_of_msg_for_repairmen.values()):
        server.sendmail(fromaddr, repairman.email, repairman_msg)
    server.close()


def calculate_repairman_average_rate(repairman_id):
    user = User(
        id=repairman_id,
        rating=Event.get_repairman_avg_rating(repairman_id))
    user.save_avg_rating()


def calculate_xp(rate, price, repairman_id):
    xp_value_factor = lookup_rate_xp.get(int(rate))
    #xp_price_factor = lookup_pricedigit_rate.get(len(str(int(price))))
    if User.get(repairman_id).xp != None:
        xp = User.get(repairman_id).xp
    else:
        xp = 0
    #xp = xp + (xp_value_factor * xp_price_factor)
    xp = xp + xp_value_factor
    level = calculate_level(xp)
    save_xp_lvl_in_database(xp, level, repairman_id)


def calculate_level(xp):
    levels = lookuptable_level_xp.keys()
    levels.sort()
    level = 0
    for lvl in levels:
        if xp <= lvl:
            level = lookuptable_level_xp.get(lvl)
            break
    return (level-1)


def save_xp_lvl_in_database(xp, level, repairman_id):
    user = User(
        id=repairman_id,
        xp=xp,
        level=level
    )
    user.save_lvl_xp()


lookuptable_level_xp = {
    0: 1,
    100: 2,
    300: 3,
    600: 4,
    1000: 5,
    1500: 6,
    2100: 7,
    2800: 8,
    3600: 9,
    4500: 10,
    5500: 11,
    6500: 12,
    7500: 13,
    8500: 14,
    10000: 15,
    12000: 16,
    14000: 17,
    16000: 18,
    18500: 19,
    21000: 20
}


lookup_rate_xp = {
    5: 500,
    4: 400,
    3: 100,
    2: -50,
    1: -100
}


lookup_pricedigit_rate = {
    1: 1,
    2: 1,
    3: 2,
    4: 3,
    5: 5
}


lookup_color_levels = {
    1: ('#ff5c33', '#ff3300'),
    2: ('#86b242', '#6fad10'),
    3: ('#b23380', '#ad106f'),
    4: ('#008fc6', '#46a1c4')
}


app.register_blueprint(bp)
