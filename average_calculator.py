from flask import Flask, jsonify
import requests
import time
import threading
import os

app = Flask(__name__)

WINDOW_SIZE = 10
numbers_store = []
lock = threading.Lock()

API_URLS = {
    'p': os.getenv('PRIME_API_URL', 'http://20.244.56.144/evaluation-service/primes'),
    'f': os.getenv('FIBO_API_URL', 'http://20.244.56.144/evaluation-service/fibo'),
    'e': os.getenv('EVEN_API_URL', 'http://20.244.56.144/evaluation-service/even'),
    'r': os.getenv('RAND_API_URL', 'http://20.244.56.144/evaluation-service/rand')
}

def fetch_numbers(number_id):
   def fetch_numbers(number_id):
    start_time = time.time()
    try:
        response = requests.get(API_URLS[number_id], timeout=0.5)
        print(f"Fetching from {API_URLS[number_id]}: Status Code {response.status_code}")  # Debugging line
        if response.status_code == 200:
            return response.json().get('numbers', [])
        else:
            app.logger.error(f"Failed to fetch numbers: {response.status_code}")
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Request failed: {str(e)}")
    return []


@app.route('/numbers/<string:number_id>', methods=['GET'])
def get_numbers(number_id):
    if number_id not in API_URLS:
        return jsonify({"error": "Invalid number ID"}), 400

    fetched_numbers = fetch_numbers(number_id)

    with lock:
        for number in fetched_numbers:
            if number not in numbers_store:
                if len(numbers_store) >= WINDOW_SIZE:
                    numbers_store.pop(0)  
                numbers_store.append(number)

        if len(numbers_store) > 0:
            avg = sum(numbers_store) / len(numbers_store)
        else:
            avg = 0.0

        response = {
            "windowPrevState": numbers_store[:-1] if len(numbers_store) > 0 else [],
            "windowCurrState": numbers_store,
            "numbers": fetched_numbers,
            "avg": round(avg, 2)
        }

    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9876, debug=True)
