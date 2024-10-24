from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from flask_caching import Cache

# Konfiguracja aplikacji Flask
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("URI")
app.config['CACHE_TYPE'] = 'simple'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300

db = SQLAlchemy(app)
cache = Cache(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    balance_pln = db.Column(db.Float, nullable=False)
    balance_tokens = db.Column(db.Float, nullable=False)

class Tokens(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Float, nullable=False)

@app.route('/')
def index():
    userlogged = cache.get('user-logged')
    return render_template('index.html', user=userlogged)

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Sprawdź, czy użytkownik już istnieje
        existing_user = Users.query.filter_by(name=email).first()
        if existing_user is None:
            # Dodanie nowego użytkownika z domyślnymi wartościami dla PLN i tokenów
            new_user = Users(name=email, password=password, balance_pln=100, balance_tokens=0)
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('index'))  # Przekierowanie na stronę główną po rejestracji
        else:
            return "Użytkownik już istnieje!"
    
    return render_template('register.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Sprawdź, czy użytkownik istnieje
        user = Users.query.filter_by(name=email, password=password).first()
        if user is not None:
            # Zapisz email do cache
            cache.set('user-logged', email)
            
            return redirect(url_for('index'))  # Przekierowanie na stronę główną po zalogowaniu
        else:
            return "Nieprawidłowy email lub hasło!"
    
    return render_template('login.html')

@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard():
    userlogged = cache.get('user-logged')
    
    # Sprawdź czy userlogged nie jest None
    if userlogged is None:
        return redirect(url_for('login'))
    
    print(f"User logged: {userlogged}")  # Debugowanie, aby zobaczyć wartość userlogged
    
    # Pobranie użytkownika z bazy danych
    user = Users.query.filter_by(name=userlogged).first()
    
    if user is None:
        return "Błąd: użytkownik nie znaleziony!"
    
    balancepln = user.balance_pln
    balancetokens = user.balance_tokens
    print(f"Balance PLN: {balancepln}")
    print(f"Balance tokens: {balancetokens}")
    
    return render_template('dashboard.html', balancepln=balancepln, balancetokens=balancetokens, user=userlogged)

        
if __name__ == '__main__':
    app.run(debug=False)
