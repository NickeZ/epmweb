#!/usr/bin/python3
"""This is the server for EPM"""
from datetime import datetime
import subprocess
import tempfile
import toml
import os
import json
import re
import sqlite3

# External imports
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from flask import Flask, request, redirect, url_for, jsonify
from flask_api import status
from werkzeug.utils import secure_filename

# External local imports
from db.db import Package, Version, User

DB = '../db/production.db'
UPLOAD_FOLDER = '../public_html/packages'
ALLOWED_EXTENSIONS = ['tar.gz']

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

engine = sqlalchemy.create_engine('sqlite:///{}'.format(DB), echo=True)
Session = sessionmaker(bind=engine)

@app.route("/")
def hello():
    result = "Hello world!<br>\n"
    session = Session()
    for package in session.query(Package).order_by(Package.id):
        result += "{}<br>\n".format(package)

    result += "Goodbye, cruel world!\n"
    return result

def allowed_file(filename):
    return '.' in filename and (
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS or
            '.'.join(filename.rsplit('.', 2)[1:]) in ALLOWED_EXTENSIONS)

@app.route("/api/v1/packages", methods=['GET'])
def packages_list():
    session = Session()
    result = []
    for package in session.query(Package).order_by(Package.id):
        versions = [str(x) for x in session.query(Version).filter_by(package_id=package.id)]
        result.append({'package':"{}".format(package), 'versions':versions})
    return jsonify(result)

def error(message):
    return jsonify({'code': 400, 'message': message}), status.HTTP_400_BAD_REQUEST

def ok(message):
    return jsonify({'code': 200, 'message': message})

@app.route('/api/v1/users/new', methods=['POST'])
def users_new():
    print(request.form)
    if 'email' not in request.form.keys():
        return error('Missing email')
    session = Session()
    session.add(User(email=request.form['email']))
    try:
        session.commit()
    except sqlalchemy.exc.IntegrityError as why:
        return error('Email already exists')
    return ok('Registered user')

@app.route('/api/v1/users', methods=['GET'])
def users_list():
    session = Session()
    res = []
    for user in session.query(User):
        res.append('{}'.format(user))
    return jsonify(res)


@app.route("/api/v1/packages/new", methods=['PUT'])
def packages_new():
    if 'project' not in request.files:
        return error('No files part')
    file = request.files['project']
    if file.filename == '':
        return error('Empty filename')
    if file and allowed_file(file.filename):
        session = Session()
        filename = secure_filename(file.filename)
        final_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(final_filename)
        temporary_dir = tempfile.mkdtemp()
        subprocess.call('tar xf {} -C {}'.format(final_filename, temporary_dir), shell=True)
        with open(os.path.join(temporary_dir, 'Epm.toml'), 'r') as tomlfile:
            manifest = toml.loads(tomlfile.read())
        for author in manifest['project']['authors']:
            matches = re.search(r'<(.*)>', author)
            if matches:
                email = matches.group(1)
            else:
                return error('Invalid author information')
            user = session.query(User).filter_by(email=email).first()
            if user:
                break
        else:
            return error('User not registered')
        if 'description' in manifest['project']:
            desc = manifest['project']['description']
        else:
            desc = None
        if 'repository' in manifest['project']:
            repo = manifest['project']['repository']
        else:
            repo = None
        pak = session.query(Package).filter_by(name=manifest['project']['name']).first()
        if not pak:
            pak = Package(
                user_id=user.id,
                name=manifest['project']['name'],
                max_version=manifest['project']['version'],
                description=desc,
                repository=repo,
            )
            session.add(pak)
            session.commit()
        else:
            pak.max_version = manifest['project']['version']
            pak.description = desc
            pak.repository = repo
            pak.updated = datetime.now()
        session.add(Version(
            package_id=pak.id,
            version=manifest['project']['version']
        ))
        session.commit()
    return ok('Uploaded!')

if __name__ == "__main__":
    app.run(debug=True)
