# Simple Stock Exchange

A very simple stock market simulation.

## User Dashboard

**Current Price and Market Cap of everything being traded:**

![Dashboard Screenshot](https://github.com/user-attachments/assets/c8341449-976e-4506-8213-ecfd27b6cbf5)

---

**The Orderbook System:**

![Orderbook Screenshot](https://github.com/user-attachments/assets/e571cf9b-e88c-4899-aebf-7fc1c4c86715)

---

**Linechart visualisations of commodity prices over time:**

![Linechart 1](https://github.com/user-attachments/assets/ba10eeef-5451-4bae-aef9-765cc6c09361)
![Linechart 2](https://github.com/user-attachments/assets/22256f6a-9483-4d4e-9515-491eea1246e3)

---

## Admin Panel

**A unified dashboard for everything:**

![Admin Dashboard](https://github.com/user-attachments/assets/1f6fbe53-ec2e-4277-9697-9743e32dc61c)

---

**Simulate IPOs by issuing new stocks and allotting a set amount of stocks to any user:**

![IPO Simulation](https://github.com/user-attachments/assets/5fa45e2d-0a1c-4496-ae37-e9e2d56b4cd1)

---

## How It Works

The system maintains an order book with two sides:
- **Bids**: Buy orders sorted by price (highest first)
- **Asks**: Sell orders sorted by price (lowest first)
And then we match them.

## How to Run

### Prerequisites
```bash
pip install -r requirements.txt
```

### Start the Server
```bash
python run_server.py
```

The server will start on `http://localhost:5001`

### Login
- **Regular users**: Enter any username/password (account created automatically)
- **Admin**: Username: `admin`, Password: `adminpass`

## Load Testing

### Benchmark
To run the benchmark client:
```bash
python src/benchmark_client.py
```
You'll be prompted to enter the maximum number of clients and orders/sec to test.
