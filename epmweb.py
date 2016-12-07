#!/usr/bin/python3
"""This is the server for EPM"""
from datetime import datetime
import sqlite3
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from flask import Flask
app = Flask(__name__)

from db.db import Package

DB = '../db/production.db'

engine = sqlalchemy.create_engine('sqlite:///{}'.format(DB), echo=True)
Session = sessionmaker(bind=engine)

@app.route("/")
def hello():
    result = "Hello world!\n"
    session = Session()
    for package in session.query(Package).order_by(Package.id):
        result += "{} {}\n".format(package.created, package.name)

    result += "Goodbye, cruel world!\n"
    return result

@app.route("/api/v1/packages/new", methods=['PUT'])
def upload_new_package():
    session = Session()
    now = datetime.now()
    session.add(Package(
        name="test",
        updated=now,
        created=now,
        description='testtest',
    ))
    session.commit()
    return "uploaded!"

if __name__ == "__main__":
    app.run()
