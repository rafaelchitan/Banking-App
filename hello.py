from flask import Flask, render_template, redirect, url_for, request, jsonify, session
from flask_pymongo import PyMongo
import pymongo 
from user.models import User, Card, Transaction
from database import db
import random

app = Flask(__name__)

app.secret_key = b'\xcc^\x91\xea\x17-\xd0W\x03\xa7\xf8J0\xac8\xc5'

user = User()  # Create an instance of the User class

@app.route('/accounts', methods=['GET'])
def accounts():
    if 'username' in session:
        user_id = session.get('user_id')
        user_data = db.users.find_one({"_id": user_id})

        if user_data:
            accounts = user_data.get('accounts', [])
            return render_template('accounts.html', username=session['username'], accounts=accounts)
        else:
            return render_template('accounts.html', username=session['username'], accounts=[])

    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        return user.signup()  # Use the signup method of the User class

    return render_template('register.html')

def get_user_from_database(user_id):
    # Query the database for the user
    user_data = db.users.find_one({'_id': user_id})

    # Create a new User object from the returned data
    dataUser = User.from_dict(user_data)
    
    return dataUser

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Authenticate the user. This will depend on how your User class is implemented.
        user.login()
        
        return redirect(url_for('home'))

    return render_template('login.html', error="Invalid username or password")

@app.route('/logout', methods=['GET'])
def logout():
    return user.signout()  # Use the signout method of the User class

@app.route('/', methods=['GET'])
def home():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/buttons', methods=['GET'])
def buttons():
    if 'username' in session:
        return render_template('buttons.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/debitcards', methods=['GET'])
def debitcards():
    if 'username' in session:
        user_id = session.get('user_id')
        user_data = db.users.find_one({"_id": user_id})

        if user_data:
            accounts = user_data.get('accounts', [])
            return render_template('debitcards.html', username=session['username'], accounts=accounts)
        else:
            return render_template('debitcards.html', username=session['username'], accounts=[])

    return redirect(url_for('login'))

def generate_iban():
    bank_code = 'BANK'
    account_number = ''.join(random.choice('0123456789') for _ in range(10))
    return 'RO00' + bank_code + account_number

@app.route('/request_account', methods=['POST'])
def request_account():
    # Handle the form submission
    data = request.get_json()
    alias = data.get('alias')
    currency = data.get('currency')
    
    if not alias or not currency:
        return jsonify({'message': 'Invalid request'}), 400

    iban = generate_iban()

    if not iban:
        return jsonify({'message': 'Could not generate IBAN'}), 500

    # Get the currently logged in user
    user_id = session.get('user_id')
    if user_id is None:
        return jsonify({'message': 'Not logged in'}), 401

    user = get_user_from_database(user_id)

    # Add the new account to the user
    user.add_account(alias, currency, iban)
    print(user.accounts)

    return jsonify({'message': 'Account created successfully'}), 200
  
# Luhn algorithm / mod 10 algorithm  
def generate_card_number():
  card_number = [random.randint(1, 9) for _ in range(15)]
  card_number = [int(digit) for digit in card_number]
  for i in range(0, 15, 2):
      card_number[i] = card_number[i] * 2
      if card_number[i] > 9:
          card_number[i] -= 9
  check_digit = 10 - (sum(card_number) % 10)
  if check_digit == 10:
      check_digit = 0
  card_number.append(check_digit)
  return ''.join(map(str, card_number)) 
  

@app.route('/request_card', methods=['POST'])
def request_card():
    data = request.get_json()
    firstName = data['firstName']
    lastName = data['lastName']
    iban = data['iban']

    # Get the user_id from the session
    user_id = session.get('user_id')

    # Fetch the user from the database
    user = db.users.find_one({"_id": user_id})

    # Check if the user's account's IBAN matches the provided IBAN
    account = [account for account in user['accounts'] if account['iban'] == iban]
    if account:
        # Generate a new card number
        card_number = generate_card_number()

        # Create a new card
        card = Card(firstName=firstName, lastName=lastName, number=card_number, iban=iban, user_id=user_id)

        # Add the card to the user's account
        db.users.update_one(
            {"_id": user_id, "accounts.iban": iban},
            {"$push": {"accounts.$.cards": card.to_dict()}}
        )

        return jsonify({'message': 'Card created successfully'}), 200

    return jsonify({'message': 'Invalid IBAN'}), 400

@app.route('/display', methods=['GET'])
def display():
    if 'username' in session:
        user_id = session.get('user_id')
        user_data = db.users.find_one({"_id": user_id})

        if user_data:
            accounts = user_data.get('accounts', [])
            return render_template('display.html', username=session['username'], accounts=accounts)
        else:
            return render_template('display.html', username=session['username'], accounts=[])

    return redirect(url_for('login'))


@app.route('/transfer_money', methods=['POST'])
def transfer_money():
    # Handle the form submission
    data = request.get_json()
    senderIBAN = data.get('senderIBAN')
    receiverIBAN = data.get('receiverIBAN')
    amount = data.get('amount')
    
    if not senderIBAN or not receiverIBAN or not amount:
        return jsonify({'message': 'Invalid request'}), 400

    # Get the currently logged in user
    user_id = session.get('user_id')
    if user_id is None:
        return jsonify({'message': 'Not logged in'}), 401
    
    transaction = Transaction(senderIBAN, receiverIBAN, amount)
    transaction.save_to_db()

    return jsonify({'message': 'Account created successfully'}), 200


app.run(debug=False, port=5000)