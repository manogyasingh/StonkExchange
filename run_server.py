from src.app import app

if __name__ == '__main__':
    print("Starting StonkExchange server...")
    app.run(host='127.0.0.1', port=5001, debug=False) 