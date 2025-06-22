from flask import Flask, request, render_template, jsonify, session, redirect, url_for
from functools import wraps
import secrets
from datetime import datetime
import os
import json
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Data storage paths
DATA_DIR = '../data'
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
STOCKS_FILE = os.path.join(DATA_DIR, 'stocks.json')
ORDERBOOK_FILE = os.path.join(DATA_DIR, 'orderbook.json')
PRICE_HISTORY_FILE = os.path.join(DATA_DIR, 'price_history.json')
TOTAL_MINTED_FILE = os.path.join(DATA_DIR, 'total_minted.json')

os.makedirs(DATA_DIR, exist_ok=True)

def save_data():
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f)
        with open(STOCKS_FILE, 'w') as f:
            json.dump(STOCKS, f)
        with open(ORDERBOOK_FILE, 'w') as f:
            json.dump(orderbook, f)
        with open(PRICE_HISTORY_FILE, 'w') as f:
            json.dump(price_history, f)
        with open(TOTAL_MINTED_FILE, 'w') as f:
            json.dump(total_minted, f)
    except Exception as e:
        print(f"Error saving data: {e}")

def load_data():
    global users, STOCKS, orderbook, price_history, total_minted
    users = {}
    STOCKS = []
    orderbook = {}
    price_history = {}
    total_minted = {}
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE) as f:
                users = json.load(f)
        if os.path.exists(STOCKS_FILE):
            with open(STOCKS_FILE) as f:
                STOCKS = json.load(f)
        if os.path.exists(ORDERBOOK_FILE):
            with open(ORDERBOOK_FILE) as f:
                orderbook = json.load(f)
        if os.path.exists(PRICE_HISTORY_FILE):
            with open(PRICE_HISTORY_FILE) as f:
                price_history = json.load(f)
        if os.path.exists(TOTAL_MINTED_FILE):
            with open(TOTAL_MINTED_FILE) as f:
                total_minted = json.load(f)
        else:
            if STOCKS:
                total_minted = {symbol: 0 for symbol in STOCKS}
    except Exception as e:
        print(f"Error loading data: {e}")

load_data()

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = generate_password_hash('adminpass')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session or session.get('username') != ADMIN_USERNAME:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def validate_stock_symbol(symbol: str) -> bool:
    return symbol.isalpha() and symbol.isupper() and len(symbol) <= 5

def validate_quantity(quantity: int) -> bool:
    return isinstance(quantity, int) and quantity > 0

def match_orders(symbol: str):
    if symbol not in orderbook:
        return
        
    while (len(orderbook[symbol]['bids']) > 0 and 
           len(orderbook[symbol]['asks']) > 0 and 
           orderbook[symbol]['bids'][0][0] >= orderbook[symbol]['asks'][0][0]):
        
        bid = orderbook[symbol]['bids'][0]
        ask = orderbook[symbol]['asks'][0]
        price = ask[0]
        quantity = min(bid[1], ask[1])
        
        trade_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if symbol not in price_history:
            price_history[symbol] = []
        price_history[symbol].append({'time': trade_time, 'price': price})
        
        buyer = bid[2]
        users[buyer]['balance'] -= price * quantity
        users[buyer]['stocks'][symbol] = users[buyer]['stocks'].get(symbol, 0) + quantity
        
        seller = ask[2]
        users[seller]['balance'] += price * quantity
        users[seller]['stocks'][symbol] -= quantity
        
        bid[1] -= quantity
        ask[1] -= quantity
        
        if bid[1] == 0:
            orderbook[symbol]['bids'].pop(0)
        if ask[1] == 0:
            orderbook[symbol]['asks'].pop(0)
        
        save_data()

@app.route('/')
@login_required
def index():
    return render_template('index.html', 
                         user=users[session['username']], 
                         orderbook=orderbook,
                         stocks=STOCKS,
                         total_minted=total_minted,
                         price_history=price_history)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == ADMIN_USERNAME:
            if check_password_hash(ADMIN_PASSWORD, password):
                session['username'] = username
                session['is_admin'] = True
                return redirect(url_for('admin_dashboard'))
            return 'Invalid password'
        
        if username in users:
            if check_password_hash(users[username]['password'], password):
                session['username'] = username
                session['is_admin'] = False
                return redirect(url_for('index'))
            return 'Invalid password'
        
        initial_stocks = {symbol: 0 for symbol in STOCKS}
        users[username] = {
            'password': generate_password_hash(password),
            'balance': 10000.0,
            'stocks': initial_stocks
        }
        session['username'] = username
        session['is_admin'] = False
        save_data()
        return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/place_order', methods=['POST'])
@login_required
def place_order():
    username = session['username']
    symbol = request.form['symbol'].upper()
    order_type = request.form['type']

    if not validate_stock_symbol(symbol) or symbol not in STOCKS:
        return jsonify({'status': 'error', 'message': 'Invalid stock symbol'})

    try:
        price = float(request.form['price'])
        quantity = int(request.form['quantity'])
        
        if not validate_quantity(quantity):
            return jsonify({'status': 'error', 'message': 'Invalid quantity'})
            
        if price <= 0:
            return jsonify({'status': 'error', 'message': 'Price must be positive'})
            
        if order_type == 'bid':
            if users[username]['balance'] < price * quantity:
                return jsonify({'status': 'error', 'message': 'Insufficient funds'})
            if symbol not in orderbook:
                orderbook[symbol] = {'bids': [], 'asks': []}
            orderbook[symbol]['bids'].append([price, quantity, username])
            orderbook[symbol]['bids'].sort(key=lambda x: (-x[0], x[2]))
        else:
            if users[username]['stocks'].get(symbol, 0) < quantity:
                return jsonify({'status': 'error', 'message': 'Insufficient stocks'})
            if symbol not in orderbook:
                orderbook[symbol] = {'bids': [], 'asks': []}
            orderbook[symbol]['asks'].append([price, quantity, username])
            orderbook[symbol]['asks'].sort(key=lambda x: (x[0], x[2]))
        
        match_orders(symbol)
        save_data()
        
        return jsonify({
            'status': 'success',
            'orderbook': orderbook[symbol],
            'user': users[username],
            'price_history': price_history.get(symbol, [])
        })
    except (ValueError, TypeError):
        return jsonify({'status': 'error', 'message': 'Invalid price or quantity'})

@app.route('/admin', methods=['GET', 'POST'])
@admin_required
def admin_dashboard():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add_stock':
            new_stock = request.form['stock_symbol'].upper()
            if validate_stock_symbol(new_stock) and new_stock not in STOCKS:
                STOCKS.append(new_stock)
                orderbook[new_stock] = {'bids': [], 'asks': []}
                price_history[new_stock] = []
                total_minted[new_stock] = 0
                for user in users.values():
                    user['stocks'][new_stock] = 0
                save_data()
        elif action == 'allot_stocks':
            symbol = request.form['stock_symbol'].upper()
            username = request.form['username']
            try:
                quantity = int(request.form['quantity'])
                if (validate_stock_symbol(symbol) and symbol in STOCKS and 
                    username in users and validate_quantity(quantity)):
                    users[username]['stocks'][symbol] += quantity
                    total_minted[symbol] += quantity
                    save_data()
            except (ValueError, TypeError):
                pass

    return render_template('admin_dashboard.html', 
                         stocks=STOCKS,
                         users=users,
                         total_minted=total_minted,
                         price_history=price_history)

def compute_market_cap(symbol: str) -> float:
    if price_history.get(symbol) and total_minted.get(symbol):
        last_price = price_history[symbol][-1]['price']
        market_cap = total_minted[symbol] * last_price
        return market_cap
    return 0

@app.route('/stock/<symbol>')
@login_required
def stock_dashboard(symbol: str):
    if not validate_stock_symbol(symbol) or symbol not in STOCKS:
        return "Stock not found", 404
    market_cap = compute_market_cap(symbol)
    return render_template('stock_dashboard.html',
                         symbol=symbol,
                         total_minted=total_minted,
                         price_history=price_history,
                         market_cap=market_cap)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
