# Simple Stock Exchange
A very simple stock market simulation.
## User Dashboard
![Screenshot From 2025-01-11 02-03-08](https://github.com/user-attachments/assets/c8341449-976e-4506-8213-ecfd27b6cbf5)
for Current Price and Mkt Cap of everything being traded
---
![Screenshot From 2025-01-11 02-03-55](https://github.com/user-attachments/assets/e571cf9b-e88c-4899-aebf-7fc1c4c86715)
The Orderbook System
---
![Screenshot From 2025-01-11 02-05-30](https://github.com/user-attachments/assets/ba10eeef-5451-4bae-aef9-765cc6c09361)
![Screenshot From 2025-01-11 02-05-36](https://github.com/user-attachments/assets/22256f6a-9483-4d4e-9515-491eea1246e3)
Linechart visualisations of commodity prices over time.
---
## Admin Panel
![Screenshot From 2025-01-11 02-01-59](https://github.com/user-attachments/assets/1f6fbe53-ec2e-4277-9697-9743e32dc61c)
A unified dashboard for everything
---
![Screenshot From 2025-01-11 02-02-46](https://github.com/user-attachments/assets/5fa45e2d-0a1c-4496-ae37-e9e2d56b4cd1)
You can simulate IPOs by alotting issuing new stocks and alotting a set amount of stocks to any user.

## How It Works
The system maintains an order book with two sides:
- **Bids**: Buy orders sorted by price (highest first)
- **Asks**: Sell orders sorted by price (lowest first)
And then we match them. In the words of a certain cartoon character, "Take what they give you, give away what you have to, and the difference is yours."

## How to run
```
git clone https://github.com/manogyasingh/StonkExchange
cd StonkExchange
pip install -r requirements.txt
python app.py
```
Then just go to 127.0.0.1:5001
The admin credentials are `user: admin, password: adminpass`
For other things just create an account
