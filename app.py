from flask import Flask, render_template, jsonify, request
import requests
import datetime
import re

app = Flask(__name__)



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')



@app.route('/timetable')
def timetable():
    return render_template('timetable.html')

@app.route('/menu')
def menu_page():
    return render_template('menu.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
