from flask import Flask, request, render_template, jsonify, session, redirect, url_for
from functools import wraps
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# In-memory storage
users = {}  # {username: {'password': str, 'balance': float, 'stocks': {symbol: quantity}}}

# Initialize orderbook with 10 stocks
STOCKS = ['TECH', 'CARS', 'FOOD', 'BANK', 'RETAIL', 'ENERGY', 'HEALTH', 'MEDIA', 'TELCO', 'REAL']
orderbook = {symbol: {'bids': [], 'asks': []} for symbol in STOCKS}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def match_orders(symbol):
    while (len(orderbook[symbol]['bids']) > 0 and 
           len(orderbook[symbol]['asks']) > 0 and 
           orderbook[symbol]['bids'][0][0] >= orderbook[symbol]['asks'][0][0]):
        
        bid = orderbook[symbol]['bids'][0]
        ask = orderbook[symbol]['asks'][0]
        
        price = ask[0]  # Use ask price for the transaction
        quantity = min(bid[1], ask[1])
        
        # Update buyer
        buyer = bid[2]
        users[buyer]['balance'] -= price * quantity
        users[buyer]['stocks'][symbol] = users[buyer]['stocks'].get(symbol, 0) + quantity
        
        # Update seller
        seller = ask[2]
        users[seller]['balance'] += price * quantity
        users[seller]['stocks'][symbol] -= quantity
        
        # Update orders
        bid[1] -= quantity
        ask[1] -= quantity
        
        # Remove fulfilled orders
        if bid[1] == 0:
            orderbook[symbol]['bids'].pop(0)
        if ask[1] == 0:
            orderbook[symbol]['asks'].pop(0)

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', 
                         user=users[session['username']], 
                         orderbook=orderbook,
                         stocks=STOCKS)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users:
            if users[username]['password'] == password:
                session['username'] = username
                return redirect(url_for('index'))
            return 'Invalid password'
        
        # New user registration with initial stocks
        initial_stocks = {symbol: 100 for symbol in STOCKS}  # Give 100 of each stock
        users[username] = {
            'password': password,
            'balance': 10000.0,  # Initial currency
            'stocks': initial_stocks
        }
        session['username'] = username
        return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/place_order', methods=['POST'])
@login_required
def place_order():
    username = session['username']
    symbol = request.form['symbol']
    order_type = request.form['type']  # 'bid' or 'ask'
    price = float(request.form['price'])
    quantity = int(request.form['quantity'])
    
    if order_type == 'bid':
        if users[username]['balance'] < price * quantity:
            return jsonify({'status': 'error', 'message': 'Insufficient funds'})
        orderbook[symbol]['bids'].append([price, quantity, username])
        orderbook[symbol]['bids'].sort(key=lambda x: (-x[0], x[2]))  # Sort by price (desc) and username
    else:
        if users[username]['stocks'].get(symbol, 0) < quantity:
            return jsonify({'status': 'error', 'message': 'Insufficient stocks'})
        orderbook[symbol]['asks'].append([price, quantity, username])
        orderbook[symbol]['asks'].sort(key=lambda x: (x[0], x[2]))  # Sort by price (asc) and username
    
    match_orders(symbol)
    
    return jsonify({
        'status': 'success',
        'orderbook': orderbook[symbol],
        'user': users[username]
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001)
