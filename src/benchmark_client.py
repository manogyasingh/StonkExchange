import requests
import time
import threading
import random
import statistics
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import json
import sys

class StonkExchangeClient:
    def __init__(self, base_url="http://localhost:5002", username=None):
        self.base_url = base_url
        self.session = requests.Session()
        self.username = username
        self.logged_in = False
        
    def login(self, password="password123"):
        """Login to the exchange"""
        try:
            response = self.session.post(
                f"{self.base_url}/login",
                data={"username": self.username, "password": password},
                allow_redirects=False,
                timeout=10
            )
            self.logged_in = response.status_code in [200, 302]
            return self.logged_in
        except Exception:
            return False
    
    def place_order(self, symbol, order_type, price, quantity):
        """Place a buy or sell order"""
        if not self.logged_in:
            return False
            
        try:
            response = self.session.post(
                f"{self.base_url}/place_order",
                data={
                    "symbol": symbol,
                    "type": order_type,
                    "price": price,
                    "quantity": quantity
                },
                timeout=10
            )
            if response.status_code == 200:
                result = response.json()
                return result.get("status") == "success"
        except Exception:
            pass
        return False

class LoadTestMetrics:
    def __init__(self):
        self.lock = threading.Lock()
        self.results = []
        
    def add_result(self, clients, orders_per_sec, success_rate, avg_response_time):
        with self.lock:
            self.results.append({
                "clients": clients,
                "orders_per_sec": orders_per_sec,
                "success_rate": success_rate,
                "avg_response_time": avg_response_time,
                "timestamp": datetime.now().isoformat()
            })

def setup_test_environment():
    """Setup test environment by adding stocks via admin"""
    stocks = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]
    admin_session = requests.Session()
    
    try:
        # Login as admin
        login_response = admin_session.post(
            "http://localhost:5002/login",
            data={"username": "admin", "password": "adminpass"},
            allow_redirects=False,
            timeout=10
        )
        
        if login_response.status_code not in [200, 302]:
            return False
        
        # Add stocks
        for stock in stocks:
            admin_session.post(
                "http://localhost:5002/admin",
                data={
                    "action": "add_stock",
                    "stock_symbol": stock
                },
                timeout=10
            )
        return True
    except Exception:
        return False

def run_client(client_id, duration_seconds, orders_per_second):
    """Run a single client for specified duration at target rate"""
    username = f"user_{client_id}"
    client = StonkExchangeClient("http://localhost:5002", username)
    
    # Login
    if not client.login():
        return 0, 0, []
    
    stocks = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]
    order_interval = 1.0 / orders_per_second if orders_per_second > 0 else 1.0
    
    successful_orders = 0
    total_orders = 0
    response_times = []
    
    start_time = time.time()
    next_order_time = start_time
    
    while time.time() - start_time < duration_seconds:
        if time.time() >= next_order_time:
            symbol = random.choice(stocks)
            order_type = random.choice(["bid", "ask"])
            price = round(random.uniform(50, 200), 2)
            quantity = random.randint(1, 5)
            
            order_start = time.time()
            success = client.place_order(symbol, order_type, price, quantity)
            order_time = (time.time() - order_start) * 1000
            
            response_times.append(order_time)
            total_orders += 1
            if success:
                successful_orders += 1
            
            next_order_time += order_interval
        else:
            time.sleep(0.01)  # Small sleep to avoid busy waiting
    
    success_rate = (successful_orders / total_orders) * 100 if total_orders > 0 else 0
    avg_response_time = statistics.mean(response_times) if response_times else 0
    
    return successful_orders, total_orders, response_times

def run_load_test_phase(num_clients, orders_per_second, phase_duration=30):
    """Run a single phase of the load test"""
    print(f"Testing {num_clients} clients, {orders_per_second} orders/sec for {phase_duration}s...")
    
    orders_per_client = orders_per_second / num_clients if num_clients > 0 else 0
    
    with ThreadPoolExecutor(max_workers=num_clients) as executor:
        futures = []
        for client_id in range(num_clients):
            future = executor.submit(run_client, client_id, phase_duration, orders_per_client)
            futures.append(future)
        
        # Collect results
        total_successful = 0
        total_orders = 0
        all_response_times = []
        
        for future in futures:
            successful, total, response_times = future.result()
            total_successful += successful
            total_orders += total
            all_response_times.extend(response_times)
    
    success_rate = (total_successful / total_orders) * 100 if total_orders > 0 else 0
    avg_response_time = statistics.mean(all_response_times) if all_response_times else 0
    actual_orders_per_sec = total_orders / phase_duration
    
    print(f"  ✓ Success rate: {success_rate:.1f}%")
    print(f"  ✓ Avg response: {avg_response_time:.1f}ms")
    print(f"  ✓ Actual rate: {actual_orders_per_sec:.1f} orders/sec")
    
    return success_rate, avg_response_time, actual_orders_per_sec

def gradual_load_test(max_n):
    """Run gradual load test increasing to max_n clients and orders/sec"""
    print(f"🚀 Starting gradual load test up to {max_n} clients and {max_n} orders/sec")
    print("="*60)
    
    # Check server
    try:
        response = requests.get("http://localhost:5002/login", timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding!")
            return
    except Exception:
        print("❌ Cannot connect to server!")
        return
    
    # Setup environment
    print("Setting up test environment...")
    if not setup_test_environment():
        print("❌ Failed to setup test environment!")
        return
    print("✓ Test environment ready")
    
    # Run gradual phases
    metrics = LoadTestMetrics()
    phases = []
    
    # Create gradual increase phases
    step_size = max(1, max_n // 5)  # 5 phases
    for i in range(1, 6):
        clients = min(i * step_size, max_n)
        orders_per_sec = min(i * step_size, max_n)
        phases.append((clients, orders_per_sec))
    
    print(f"\nRunning {len(phases)} phases:")
    for i, (clients, orders_per_sec) in enumerate(phases, 1):
        print(f"\n📊 Phase {i}/{len(phases)}: {clients} clients, {orders_per_sec} orders/sec")
        
        success_rate, avg_response_time, actual_rate = run_load_test_phase(
            clients, orders_per_sec, phase_duration=1
        )
        
        metrics.add_result(clients, actual_rate, success_rate, avg_response_time)
    
    # Print summary
    print("\n" + "="*60)
    print("LOAD TEST SUMMARY")
    print("="*60)
    print(f"{'Phase':<8} {'Clients':<8} {'Rate/sec':<10} {'Success%':<10} {'Avg ms':<10}")
    print("-" * 60)
    
    for i, result in enumerate(metrics.results, 1):
        print(f"{i:<8} {result['clients']:<8} {result['orders_per_sec']:<10.1f} "
              f"{result['success_rate']:<10.1f} {result['avg_response_time']:<10.1f}")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"load_test_results_{timestamp}.json"
    try:
        with open(filename, 'w') as f:
            json.dump(metrics.results, f, indent=2)
        print(f"\n💾 Results saved to: {filename}")
    except Exception as e:
        print(f"Failed to save results: {e}")
    
    # Final assessment
    final_result = metrics.results[-1]
    if final_result['success_rate'] >= 90:
        print(f"\n✅ SUCCESS: System handled {max_n} clients/{max_n} orders/sec with {final_result['success_rate']:.1f}% success")
    elif final_result['success_rate'] >= 70:
        print(f"\n⚠️  PARTIAL: System handled load with {final_result['success_rate']:.1f}% success (some degradation)")
    else:
        print(f"\n❌ FAILURE: System struggled with {final_result['success_rate']:.1f}% success rate")

def main():
    print("StonkExchange Simple Load Tester")
    print("================================")
    print("This tool gradually increases load to test your system's capacity.")
    print("It will test from 1 up to N clients and N orders per second.\n")
    
    try:
        max_n = int(input("Enter maximum number of clients and orders/sec to test (e.g., 20): "))
        if max_n <= 0:
            print("Please enter a positive number.")
            return
    except ValueError:
        print("Please enter a valid number.")
        return
    
    gradual_load_test(max_n)

if __name__ == "__main__":
    main() 