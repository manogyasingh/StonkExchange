# Simple Stock Exchange

A lightweight stock exchange simulation built with Flask. This project implements a basic automatic order book system.
## How It Works

The system maintains an order book with two sides:
- **Bids**: Buy orders sorted by price (highest first)
- **Asks**: Sell orders sorted by price (lowest first)

When orders are placed, the system automatically tries to match compatible orders:
1. If the highest bid price ≥ lowest ask price, a trade occurs
2. The trade executes at the ask price
3. The buyer's balance decreases and their stock quantity increases
4. The seller's balance increases and their stock quantity decreases

## Getting Started

1. Install the required dependencies:
   ```bash
   pip install flask
   ```

2. Run the application:
   ```bash
   python orderbook/app.py
   ```

3. Open your browser and navigate to `http://localhost:5001`

4. Login or register with a username and password

## Usage

1. **Login/Register**
   - Enter a username and password
   - New users automatically receive starting balance and stocks

2. **View Portfolio**
   - See your current balance and stock holdings at the top of the page

3. **Place Orders**
   - Select order type (Buy/Sell)
   - Enter price per stock
   - Enter quantity
   - Click "Place Order"

4. **View Order Book**
   - Buy orders are shown on the left
   - Sell orders are shown on the right
   - Each order displays price, quantity, and username
5. **Admin Panel**
   - Admin can issue stocks
6. Market Cap and Graphs
   - Market Capitalisation and a graph of past deal prices is maintained.
