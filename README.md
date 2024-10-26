# Simple Stock Exchange

A lightweight stock exchange simulation built with Flask. This project implements a basic order book system where users can trade a sample stock through a web interface.

## Features

- **Simple Authentication**: Users can login or register with just a username and password
- **Initial Portfolio**: New users receive 10,000 currency units and 1,000 SAMPLE stocks
- **Real-time Order Book**: View current buy (bid) and sell (ask) orders
- **Order Matching**: Automatic matching of compatible buy and sell orders
- **Portfolio Tracking**: Monitor your balance and stock holdings
- **Clean Web Interface**: Easy-to-use interface for placing and viewing orders

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

## Technical Details

- Built with Flask (Python web framework)
- Uses in-memory storage for user data and orders
- Implements a simple order matching algorithm
- Responsive web interface using HTML and JavaScript
- Real-time updates using AJAX calls

## Notes

- There are 10 stocks in StonkExchange ('TECH', 'CARS', 'FOOD', 'BANK', 'RETAIL', 'ENERGY', 'HEALTH', 'MEDIA', 'TELCO', 'REAL') You can change this by editing the stocks list `app.py`
- Data is stored in memory and will be reset when the server restarts
- The system uses a simple authentication system (not suitable for production)
