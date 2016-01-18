from app import db
from model import User
from model import Event


us1 = User(name='Igor',surename='Kljucaricek',username='iky',password='iky',email='igor.kljucaricek@gmail.com')
us2 = User(name='Pavel',surename='Najman',username='pavlik',password='pavlik',email='pavel.najman@gmail.com')
ev1 = Event(name='bulb',description='has 59W,5th floor,bell - cukipuki',price='555',address='Korita 44, Doly, 56546')
ev2 = Event(name='pipe',description='has 5meters,5th floor,bell - cukipuki',price='777',address='Korita 44, Dol0y, 56546')
ev3 = Event(name='wash-machine',description='exchange el. cable 2m',price='222',address='Kalupi 12, Hory, 48963')

# link 
us1.events.append(ev1)
us1.events.append(ev2)
us2.events.append(ev3)
us2.repairman = ev1

db.session.add(us1)
db.session.add(us2)
db.session.add(ev1)
db.session.add(ev2)
db.session.add(ev3)
# commit
db.session.commit()
