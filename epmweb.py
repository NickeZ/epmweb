#!/usr/bin/python3
"""This is the server for EPM"""
from datetime import datetime
import subprocess
import tempfile
import toml
import sys
import os
import errno
import shutil
import json
import re
import sqlite3
import argparse
import siphash

# External imports
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from flask import Flask, request, redirect, url_for, jsonify, render_template, send_from_directory
from flask_api import status
from flaskext.markdown import Markdown
from werkzeug.utils import secure_filename

# External local imports
from db.db import Package, Version, User

# Import config

with open('config/epmweb.toml') as configfile:
    config = toml.loads(configfile.read())

DB = os.path.join('..', config['sqlite3_db'])
UPLOAD_FOLDER = os.path.join('..', config['upload_folder'])
ALLOWED_EXTENSIONS = config['allowed_extensions']

KEY_SIPHASH = bytearray.fromhex('9664 06fe 676f 1a04 b799 059f cff6 a9a8')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = config['upload_folder']
if 'server_name' in config:
    app.config['SERVER_NAME'] = config['server_name']
app.config['PREFERRED_URL_SCHEME'] = 'https'

Markdown(app)

engine = sqlalchemy.create_engine('sqlite:///{}'.format(DB), echo=True)
Session = sessionmaker(bind=engine)

@app.route("/about")
def about():
    return render_template('text.html', title='about', message='This is a proof of concept')

@app.route("/packages/")
@app.route("/packages/<name>")
def package(name=None):
    if not name:
        return redirect(url_for('index'))
    session = Session()
    pak = session.query(Package).filter_by(name=name).first()
    if not pak:
        return render_template('404.html', message="Could not find package")
    package = {'package':pak, 'versions': session.query(Version).filter_by(package_id=pak.id).all()}

    return render_template('package.html', package=package)

@app.route("/")
def index():
    session = Session()
    paks = session.query(Package).order_by(Package.name).all()
    packages = []
    for package in paks:
        packages.append({'package':package, 'versions': session.query(Version).filter_by(package_id=package.id).all() })

    return render_template('packages.html', packages=packages)

def allowed_file(filename):
    return '.' in filename and (
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS or
            '.'.join(filename.rsplit('.', 2)[1:]) in ALLOWED_EXTENSIONS)

@app.route("/api/v1/packages/<name>/<chksum>", methods=['GET'])
def package_download(name=None, chksum=None):
    if not chksum or chksum == '':
        return error('Checksum empty')
    if not name or name == '':
        return error('Name empty')
    index_filename = os.path.join('..', 'index', 'packages', name)
    if not os.path.isfile(index_filename):
        return error('Invalid name')
    with open(index_filename) as index:
        versions = []
        for line in index:
            version = json.loads(line)
            if version['chksum'] == chksum:
                tarball_filename = '{}-{}-{}.tar.gz'.format(name, version['vers'], chksum)
                if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], tarball_filename)):
                    return send_from_directory(app.config['UPLOAD_FOLDER'], tarball_filename, as_attachment=True)
                else:
                    return error('File not found')
    return error('Package not found')


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
    return ok_data({'message': message})

def ok_data(data):
    return jsonify({'code' : 200, 'data': data})

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

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as why:
        if why.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

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
        tmp_dir = tempfile.mkdtemp()
        mkdir_p(os.path.join(tmp_dir, 'content'))
        tmp_filename = os.path.join(tmp_dir, filename)
        file.save(tmp_filename)
        with open(tmp_filename, 'rb') as package:
            chksum = siphash.SipHash_2_4(KEY_SIPHASH, package.read()).hexdigest()
        subprocess.call('tar xf {} -C {}'.format(tmp_filename, os.path.join(tmp_dir, 'content')), shell=True)
        with open(os.path.join(tmp_dir, 'content', 'Epm.toml'), 'r') as tomlfile:
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
        if 'name' in manifest['project']:
            name = manifest['project']['name']
        else:
            return error('Missing name in manifest file')
        if 'version' in manifest['project']:
            version = manifest['project']['version']
        else:
            return error('Missing version in manifest file')
        pak = session.query(Package).filter_by(name=name).first()
        if not pak:
            pak = Package(
                user_id=user.id,
                name=name,
                max_version=version,
                description=desc,
                repository=repo,
            )
            session.add(pak)
            session.commit()
        else:
            pak.max_version = version
            pak.description = desc
            pak.repository = repo
            pak.updated = datetime.now()
        session.add(Version(
            package_id=pak.id,
            version=version
        ))
        session.commit()
    shutil.move(tmp_filename, os.path.join(app.config['UPLOAD_FOLDER'], '{}-{}-{}.tar.gz'.format(name, version, chksum.decode('utf-8'))))
    return ok_data({'message': 'Uploaded!', 'chksum': chksum.decode('utf-8')})

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug',  action='store_true')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', default=5000)
    args = parser.parse_args(sys.argv[1:])
    if args.debug:
        app.run(debug=True, host=args.host, port=int(args.port))
    else:
        app.run(host=args.host, port=int(args.port))
