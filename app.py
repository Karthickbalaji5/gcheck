from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret_banking_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bank.db'
db = SQLAlchemy(app)

# --- DATABASE MODELS (OOP) ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    balance = db.Column(db.Float, default=1000.0)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(80))
    receiver = db.Column(db.String(80))
    amount = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# --- ROUTES ---
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user = User(
            username=request.form['username'],
            password=request.form['password'],
            balance=1000.0  # Starting bonus
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/auth', methods=['POST'])
def auth():
    user = User.query.filter_by(username=request.form['username'], 
                                password=request.form['password']).first()
    if user:
        session['user_id'] = user.id
        return redirect(url_for('dashboard'))
    return "Invalid Credentials", 401

@app.route('/dashboard')
def dashboard():
    user = User.query.get(session['user_id'])
    history = Transaction.query.filter((Transaction.sender == user.username) | 
                                      (Transaction.receiver == user.username)).all()
    return render_template('dashboard.html', user=user, history=history)

@app.route('/transfer', methods=['POST'])
def transfer():
    amount = float(request.form['amount'])
    recipient_name = request.form['recipient']
    sender = User.query.get(session['user_id'])
    recipient = User.query.filter_by(username=recipient_name).first()

    if recipient and sender.balance >= amount:
        sender.balance -= amount
        recipient.balance += amount
        new_tx = Transaction(sender=sender.username, receiver=recipient.username, amount=amount)
        db.session.add(new_tx)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return "Transfer Failed", 400

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Creates the database file
    app.run(debug=True)