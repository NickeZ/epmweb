#!/usr/bin/python3
"""This is the server for EPM"""
from datetime import datetime
import subprocess
import tempfile
import toml
import os
import json
import sqlite3
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from flask import Flask, request, redirect, url_for, jsonify
from flask_api import status
from werkzeug.utils import secure_filename
from db.db import Package

DB = '../db/production.db'
UPLOAD_FOLDER = '../public_html/packages'
ALLOWED_EXTENSIONS = ['tar.gz']

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

def allowed_file(filename):
    return '.' in filename and (
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS or
            '.'.join(filename.rsplit('.', 2)[1:]) in ALLOWED_EXTENSIONS)

@app.route("/api/v1/packages", methods=['GET'])
def packages_list():
    session = Session()
    result = []
    for package in session.query(Package).order_by(Package.id):
        result.append("{} {} {}".format(package.created, package.name, package.max_version))
    return jsonify(result)

def error(message):
    return jsonify({'code': 400, 'message': message}), status.HTTP_400_BAD_REQUEST

def ok(message):
    return jsonify({'code': 200, 'message': message})

@app.route("/api/v1/packages/new", methods=['PUT'])
def packages_new():
    if 'project' not in request.files:
        return error('No files part')
    file = request.files['project']
    if file.filename == '':
        return error('Empty filename')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        final_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(final_filename)
        temporary_dir = tempfile.mkdtemp()
        subprocess.call('tar xf {} -C {}'.format(final_filename, temporary_dir), shell=True)
        with open(os.path.join(temporary_dir, 'Epm.toml'), 'r') as tomlfile:
            manifest = toml.loads(tomlfile.read())
        session = Session()
        now = datetime.now()
        if 'description' in manifest['project']:
            desc = manifest['project']['description']
        else:
            desc = None
        if 'repository' in manifest['project']:
            repo = manifest['project']['repository']
        else:
            repo = None
        session.add(Package(
            name=manifest['project']['name'],
            updated=now,
            created=now,
            max_version=manifest['project']['version'],
            downloads=0,
            description=desc,
            repository=repo,
        ))
        session.commit()
    return ok('Uploaded!')

if __name__ == "__main__":
    app.run(debug=True)
