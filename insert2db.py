from app import db
from model import User
from model import Event
from model import Signedup


us1 = User(name='Igor',surename='Kljucaricek',username='iky',password='iky',email='igor.kljucaricek@gmail.com',rating='5.0')
us2 = User(name='Pavel',surename='Najman',username='pavlik',password='pavlik',email='pavel.najman@gmail.com',rating='2.0')
us3 = User(name='Tora',surename='Baskiera',username='Torator',password='tora',email='tora@gmail.com',rating='3.4')
us4 = User(name='Toby',surename='Najman',username='Tobator',password='toby',email='toby@gmail.com',rating='3.4')
us5 = User(name='Dusty',surename='Kljucaricek',username='Dusturbator',password='dusty',email='dusty@gmail.com',rating='3.4')
us6 = User(name='Windy',surename='Kljucaricek',username='Wind-chun',password='windy',email='windy@gmail.com',rating='3.4')
ev1 = Event(name='bulb',description='has 59W,5th floor,bell - cukipuki',price='555',address='Korita 44, Doly, 56546')
ev2 = Event(name='pipe',description='has 5meters,5th floor,bell - cukipuki',price='777',address='Korita 44, Dol0y, 56546')
ev3 = Event(name='wash-machine',description='exchange el. cable 2m',price='222',address='Kalupi 12, Hory, 48963')

# link 
us1.events.append(ev1)
us1.events.append(ev2)
us2.events.append(ev3)

# link1 = Signup(event_id=ev1.id,signedup_id=us3.id)
link2 = Signedup()
 
# link2.event_id = ev1
us4.signedupu.append(link2)
ev1.signedupe.append(link2)
 

# us3.repairman = ev1
# us3.repairman = ev2


db.session.add(us1)
db.session.add(us2)
db.session.add(us3)
db.session.add(us4)
db.session.add(us5)
db.session.add(us6)
db.session.add(ev1)
db.session.add(ev2)
db.session.add(ev3)
db.session.add(link2)


# commit
db.session.commit()



# link1 = Signup(event_id=ev1.id,signedup_id=us3.id)
# link2 = Signup()
# db.session.add(link1)

# db.session.commit()

