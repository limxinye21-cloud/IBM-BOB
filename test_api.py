"""Quick test script to check API"""
import requests
import json
from data.mock.generator import MockDataGenerator

# Test health
print("Testing health endpoint...")
response = requests.get("http://localhost:8000/health")
print(f"Health: {response.json()}\n")

# Test ML status
print("Testing ML status...")
response = requests.get("http://localhost:8000/api/v1/ml/status")
print(f"ML Status: {response.json()}\n")

# Generate test data
print("Generating test data...")
generator = MockDataGenerator()
data = generator.generate_single()
data_dict = data.to_dict()
print(f"Generated data keys: {list(data_dict.keys())[:10]}...\n")

# Test prediction
print("Testing prediction...")
try:
    response = requests.post(
        "http://localhost:8000/api/v1/ml/predict",
        json=data_dict,
        timeout=10
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Prediction: {response.json()}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {e}")

# Made with Bob
