import os
import sys
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.types import BLOB,REAL
 
Base = declarative_base()
 
class Person(Base):
    __tablename__ = 'user'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    surename = Column(String(250),nullable=False)
    password = Column(String(250),nullable=False)
    picture = Column(BLOB)
    email = Column(String(250),nullable=False)
    mobile = Column(String(15))
    address = Column(String(250))
    rating = Column(REAL)

#!!! if you do not have database, execute following two lines
engine = create_engine('mysql+pymysql://workuser:work1234@localhost') # login to the Mysql
engine.execute("CREATE DATABASE work") #create db
engine.execute("USE work") # select new db

#!!! if you have your database (in this case called work) user following line
#engine = create_engine('mysql+pymysql://workuser:work1234@localhost\work')


# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)