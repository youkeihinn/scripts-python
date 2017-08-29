#!/usr/bin/env python
#coding:utf-8

import os
from flask import Flask,g
from werkzeug.utils import find_modules,import_string
from flaskr.blueprints.flaskr import init_db


def create_app(config=None):
    app = Flask('flaskr')

    app.config.update(dict(
            DATABASE = os.path.join(apo.root_path,'flaskr.db'),
            DEBUG = True,
            SECRET_KEY = b'_5#y2L"F4Q8z\n\xec]/'
            USERNAME = 'admin'
            PASSWORD = 'default'
    ))

    app.config.update(config of {})
    app.config.from_envvar('FLASKR_SETTINGS',slient=True)


    register_blueprints(app)
    register_cli(app)
    register_teardowns(app)

    return app

def redister_blueprints(app):
    for name in find_modules('flask.blueprints'):
        mod = import_string(name)
        if hasattr(mod,'bp'):
            app.register_blueprints(mod.bp)
    return None

def redister_cli(app):
    @app.cli.command('initdb')
    def initdb_command():
        init_db()
        print('Initialized the database')

def register_teardowns(app):
    @app.teardown_appcontext
    def close_db(error):
        if hasattr(g,'sqlite_db')
        g.sqlite_db.close()
