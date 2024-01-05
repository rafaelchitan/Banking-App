from flask import Flask, jsonify, request, session, redirect
from passlib.hash import pbkdf2_sha256
from database import db
import uuid
from pymongo import MongoClient

class User:
  def __init__(self, _id=None):
    self._id = _id
    self.accounts = []
    self.client = MongoClient('mongodb://localhost:27017/')
    self.db = self.client['bank']
    
  @classmethod
  def from_dict(cls, data):
      user = cls(data['_id'])
      user.accounts = data.get('accounts', [])
      return user

  def add_account(self, alias, currency, iban):
    account = {
        'alias': alias,
        'currency': currency,
        'iban': iban,
        'balance': 0.0,
    }
    self.accounts.append(account)
    self.save_to_db()
    
  def save_to_db(self):
    self.db.users.update_one({'_id': self._id}, {'$set': {'accounts': self.accounts}}, upsert=True)
    
  @classmethod
  def load_from_db(cls, user_id):
      client = MongoClient('mongodb://localhost:27017/')
      db = client['bank']
      user_data = db.users.find_one({'_id': user_id})
      return cls.from_dict(user_data)    

  def start_session(self, user):
    del user['password']
    session['logged_in'] = True
    session['user'] = user
    session['username'] = user['email']
    session['user_id'] = user['_id']
    return jsonify(user), 200

  def signup(self):
    print(request.form)

    # Create the user object
    user = {
      "_id": uuid.uuid4().hex,
      "first_name": request.form.get('first_name'),
      "last_name": request.form.get('last_name'),
      "email": request.form.get('email'),
      "password": request.form.get('password')
    }

    # Encrypt the password
    user['password'] = pbkdf2_sha256.encrypt(user['password'])

    # Check for existing email address
    if db.users.find_one({ "email": user['email'] }):
      return jsonify({ "error": "Email address already in use" }), 400

    if db.users.insert_one(user):
      return self.start_session(user)

    return jsonify({ "error": "Signup failed" }), 400
  
  def signout(self):
    session.clear()
    return redirect('/')
  
  def login(self):

    user = db.users.find_one({
      "email": request.form.get('username')
    })

    if user and pbkdf2_sha256.verify(request.form.get('password'), user['password']):
      return self.start_session(user)
    
    return jsonify({ "error": "Invalid login credentials" }), 401
  
  def add_money(self, account, amount):
    account['balance'] += amount
    self.save_to_db()
  
class Card:
  def __init__(self, firstName, lastName, number, iban, user_id):
      self.firstName = firstName
      self.lastName = lastName
      self.number = number
      self.iban = iban
      self.user_id = user_id

  def to_dict(self):
      return {
          "_id": uuid.uuid4().hex,
          "firstName": self.firstName,
          "lastName": self.lastName,
          "number": self.number,
          "iban": self.iban,
          "user_id": self.user_id
      } 
  
