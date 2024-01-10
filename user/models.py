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

  def add_account(self, alias, currency, iban, balance):
    account = {
        'alias': alias,
        'currency': currency,
        'iban': iban,
        'balance': 0.0,
    }
    if balance is not None:
      account['balance'] = balance
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
      return False

    if db.users.insert_one(user):
      self.start_session(user)
      return True

    return False
  
  def signout(self):
    session.clear()
    return redirect('/')
  
  def login(self):

    user = db.users.find_one({
      "email": request.form.get('username')
    })

    if user and pbkdf2_sha256.verify(request.form.get('password'), user['password']):
      self.start_session(user)
      return True
    
    return False
  
  def add_money(self, account, amount):
    account['balance'] += amount
    self.save_to_db()
  
class Card:
  def __init__(self, firstName, lastName, number, iban, user_id, cvv, expiry_date):
      self.firstName = firstName
      self.lastName = lastName
      self.number = number
      self.iban = iban
      self.user_id = user_id
      self.cvv = cvv
      self.expiry_date = expiry_date

  def to_dict(self):
      return {
          "_id": uuid.uuid4().hex,
          "firstName": self.firstName,
          "lastName": self.lastName,
          "number": self.number,
          "iban": self.iban,
          "user_id": self.user_id,
          "cvv": self.cvv,
          "expiry_date": self.expiry_date
      } 
  
class Transaction:
  def __init__(self, sender, receiver, amount, description, currency):
    self.sender = sender
    self.receiver = receiver
    self.amount = amount
    self.client = MongoClient('mongodb://localhost:27017/')
    self.db = self.client['bank']
    self.description = description
    self.currency = currency

  def to_dict(self):
      return {
          "_id": uuid.uuid4().hex,
          "sender": self.sender,
          "receiver": self.receiver,
          "amount": self.amount,
          "description": self.description,
          "currency": self.currency
      }
  
  def save_to_db(self):
    # get the user id that has the sender iban
    senderUser = db.users.find_one({"accounts.iban": self.sender})
    receiverUser = db.users.find_one({"accounts.iban": self.receiver})
    self.db.transactions.insert_one(self.to_dict())

    senderAmount = [account['balance'] for account in senderUser['accounts'] if account['iban'] == self.sender]
    receiverAmount = [account['balance'] for account in receiverUser['accounts'] if account['iban'] == self.receiver]
    if senderAmount[0] < float(self.amount):
      return 'Insufficient funds'
    
    senderAmount[0] = float(senderAmount[0]) - float(self.amount)
    receiverAmount[0] = float(receiverAmount[0]) + float(self.amount)

    if senderUser['_id'] != receiverUser['_id']:
      self.db.users.update_one({'_id': senderUser['_id']}, {'$push': {'transactions': self.to_dict()}})
  
    self.db.users.update_one({'_id': receiverUser['_id'], 'accounts.iban': self.receiver}, {'$set': {'accounts.$.balance': receiverAmount[0]}})
    self.db.users.update_one({'_id': senderUser['_id'], 'accounts.iban': self.sender}, {'$set': {'accounts.$.balance': senderAmount[0]}})
    self.db.users.update_one({'_id': receiverUser['_id']}, {'$push': {'transactions': self.to_dict()}})

class Loan:
  def __init__(self, user, amount, currency, status):
    self.user = user
    self.amount = amount
    self.currency = currency
    self.status = status
    self.client = MongoClient('mongodb://localhost:27017/')
    self.db = self.client['bank']

  def to_dict(self):
      return {
          "_id": uuid.uuid4().hex,
          "user_id": self.user,
          "amount": self.amount,
          "currency": self.currency,
          "status": self.status
      }
  
  def save_to_db(self):
    self.db.loans.insert_one(self.to_dict())

  
