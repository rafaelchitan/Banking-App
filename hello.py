from flask import Flask, render_template, redirect, url_for, request, jsonify, session
from flask_pymongo import PyMongo
import pymongo
from user.models import User  # Import the User class
from database import db  # Import the db object from the database module

app = Flask(__name__)
app.secret_key = b'\xcc^\x91\xea\x17-\xd0W\x03\xa7\xf8J0\xac8\xc5'

user = User()  # Create an instance of the User class

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        return user.signup()  # Use the signup method of the User class

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return user.login()  # Use the login method of the User class

    return render_template('login.html')

@app.route('/logout', methods=['GET'])
def logout():
    return user.signout()  # Use the signout method of the User class

app.run(debug=True, port=5000)