from flask import Flask, render_template, redirect, url_for, request, jsonify, session
from flask_pymongo import PyMongo
import pymongo 
from user.models import User, Card, Transaction, Loan
from database import db
import random
import datetime

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
        if user.signup() == True:
            return redirect(url_for('home'))
        else:
            return render_template('register.html', error='Error creating account')
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
        if user.login() == True:
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid username/password combination')
    return render_template('login.html')

@app.route('/logout', methods=['GET'])
def logout():
    return user.signout()  # Use the signout method of the User class

@app.route('/', methods=['GET'])
def home():
    if 'username' in session:
        return render_template('home.html', username=session['username'], 
                               ron_balance=get_balance(get_user_by_id(session['user_id']), 'RON'), 
                               eur_balance=get_balance(get_user_by_id(session['user_id']), 'EUR'),
                               pending_number=pending_loans_count(get_user_by_id(session['user_id'])),
                               active_number=active_loans_count(get_user_by_id(session['user_id'])),
                               transactions=db.users.find_one({"_id": session['user_id']})['transactions'],
                               loan_requests=db.loans.find({'user_id': session['user_id']}))
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

def generate_cvv():
    return ''.join(random.choice('0123456789') for _ in range(3))

def generate_expiry_date():
    month = random.choice(['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'])
    year = datetime.date.today().year + random.randint(0, 5)
    return f'{month}/{year}'

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
    user.add_account(alias, currency, iban, 0.0)
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
        card_cvv = generate_cvv()
        expiry_date = generate_expiry_date()

        # Create a new card
        card = Card(firstName=firstName, lastName=lastName, number=card_number, iban=iban, user_id=user_id, cvv=card_cvv, expiry_date=expiry_date)

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
    description = data.get('description')
    
    if not senderIBAN or not receiverIBAN or not amount:
        return jsonify({'message': 'Invalid request'}), 400

    # Get the currently logged in user
    user_id = session.get('user_id')
    if user_id is None:
        return jsonify({'message': 'Not logged in'}), 401
    
    currency = db.users.find_one({"_id": user_id, "accounts.iban": senderIBAN}, {"accounts.$": 1})['accounts'][0]['currency']
    transaction = Transaction(senderIBAN, receiverIBAN, amount, description, currency)
    transaction.save_to_db()
    return jsonify({'message': 'Account created successfully'}), 200

from flask import jsonify
from bson.objectid import ObjectId

@app.route('/get_currency', methods=['GET'])
def get_currency():
    iban = request.args.get('iban')
    if not iban:
        return jsonify({'error': 'Missing IBAN'}), 400

    user_data = db.users.find_one({"accounts.iban": iban}, {"accounts.$": 1})

    if user_data and 'accounts' in user_data and len(user_data['accounts']) > 0:
        currency = user_data['accounts'][0].get('currency')
        if currency:
            return jsonify({'currency': currency})
        else:
            return jsonify({'error': 'Currency not found for given IBAN'}), 404
    else:
        return jsonify({'error': 'Account not found for given IBAN'}), 404

def create_loan_request(user, amount, currency, status):
    loan = Loan(user, amount, currency, status)
    
    loan.save_to_db()

@app.route('/request_loan', methods=['POST'])
def request_loan():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Missing data'}), 400

    user = session.get('user_id')
    amount = data.get('amount')
    currency = data.get('currency')
    status = 'pending'

    if not user or not amount or not status or not currency:
        return jsonify({'error': 'Missing user, amount, or status'}), 400

    try:
        create_loan_request(user, amount, currency, status)
        return jsonify({'message': 'Loan request created'}), 201
    except Exception as e:
        print(f'Failed to create loan request: {e}')
        return jsonify({'error': 'Failed to create loan request'}), 500    

def get_loans():
    try:
        # Assuming you're using MongoDB and have a `loans` collection
        loans = list(db.loans.find())
        return loans
    except Exception as e:
        print(f'Failed to get loans: {e}')
        return []

@app.route('/loans', methods=['GET'])
def loans():
    if 'username' in session and session['username'] == 'bank':
        user_id = session.get('user_id')

        loans = get_loans()
        return render_template('loans.html', username=session['username'], loans=loans, func=get_user_by_id)

    return redirect(url_for('login'))

@app.route('/history', methods=['GET'])
def history():
    if 'username' in session:
        user_id = session.get('user_id')
        user_data = db.users.find_one({"_id": user_id})

        if user_data:
            transactions = user_data.get('transactions', [])
            return render_template('history.html', username=session['username'], transactions=transactions)
        else:
            return render_template('history.html', username=session['username'], transactions=[])

    return redirect(url_for('login'))

def get_user_by_id(user_id):
    try:
        user = db.users.find_one({"_id": user_id})
        return user
    except Exception as e:
        print(f'Failed to get user: {e}')
        return None

def get_user_by_iban(iban):
    try:
        user = db.users.find_one({"iban": iban})
        return user
    except Exception as e:
        print(f'Failed to get user: {e}')
        return None        
    
@app.route('/exchange', methods=['GET'])
def exchange():
    if 'username' in session:
        accounts = db.users.find_one({"_id": session['user_id']})['accounts']
        if accounts:
            return render_template('exchange.html', username=session['username'], accounts=accounts)
        return render_template('exchange.html', username=session['username'], accounts=[])
    return redirect(url_for('login'))

@app.route('/loan_approval', methods=['POST'])
def loan_approval():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Missing data'}), 400
    
    loan_id = data.get('loan_id')
    loan = db.loans.find_one({"_id": loan_id})
    currency = loan.get('currency')
    if not loan:
        return jsonify({'error': 'Loan not found'}), 404
    
    user_id = loan.get('user_id')
    user = get_user_from_database(user_id)
    print(user)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    amount = loan.get('amount')
    amount = float(amount)
    status = data.get('approval')
    if not status:
        return jsonify({'error': 'Missing status'}), 400
    
    if status == 'accepted':
        # Add the loan amount to the user's account
        user.add_account('Loan account', currency, generate_iban(), amount)
        

    # Update the loan status
    db.loans.update_one(
        {"_id": loan_id},
        {"$set": {"status": status}}
    )
    return jsonify({'message': 'Loan modified successfully'}), 200

@app.route('/my_loans', methods=['GET'])
def my_loans():
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401
    
    user = db.users.find_one({'_id': user_id})
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    loan_requests = db.loans.find({'user_id': user_id})
    
    return render_template('my_loans.html', loan_requests=loan_requests, username=session['username'])

from flask import request, jsonify

@app.route('/delete_account', methods=['DELETE'])
def delete_account():
    user_id = session.get('user_id')
    account_iban = request.json.get('iban')

    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401

    user = db.users.find_one({"_id": user_id})

    if not user:
        return jsonify({'error': 'User not found'}), 404

    account = next((a for a in user['accounts'] if a.get('iban') == account_iban), None)
    if not account:
        return jsonify({'error': 'Account not found'}), 404

    new_accounts = [account for account in user['accounts'] if account['iban'] != account_iban]
    db.users.update_one({"_id": user['_id']}, {"$set": {"accounts": new_accounts}})

    return jsonify({'message': 'Account deleted successfully'}), 200

def get_balance(user, currency):
    balance = 0.0
    accounts = user.get('accounts', [])
    for account in accounts:
        if account.get('currency') == currency:
            balance += account.get('balance', 0.0)
    return balance

def pending_loans_count(user):
    count = 0
    loans = db.loans.find({'user_id': user['_id'], 'status': 'pending'})
    for loan in loans:
        count+=1
    return count

def active_loans_count(user):
    count = 0
    loans = db.loans.find({'user_id': user['_id'], 'status': 'accepted'})
    for loan in loans:
        count+=1
    return count

app.run(debug=False, port=5000)