#!/usr/bin/env python
# coding:utf-8
from flask import Flask
app = Flask(__name__)

@app.route('/user/<username>')
def show_user_profile(username):
    return 'User %s' % username

@app.route('/post/<int:post_id>')
def show_post(post_id):
    return 'Post %d' % post_id

@app.route('/projects/')
def projects():
    return 'The project page'

@app.route('/about')
def about():
    return 'The about page'

@app.route('/')
def index():
    return 'Index Page'

@app.route('/hello')
def hello_world():
    return "Hello World!"

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
