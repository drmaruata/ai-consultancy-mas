import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# Upstash credentials from environment variables
VECTOR_URL = os.getenv("UPSTASH_VECTOR_REST_URL")
VECTOR_TOKEN = os.getenv("UPSTASH_VECTOR_REST_TOKEN")

REDIS_URL = os.getenv("UPSTASH_REDIS_REST_URL")
REDIS_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")

QSTASH_URL = os.getenv("QSTASH_URL")
QSTASH_TOKEN = os.getenv("QSTASH_TOKEN")

def test_redis():
    print("Testing Upstash Redis...")
    # Using the Redis REST API format: /get/test_key
    headers = {"Authorization": f"Bearer {REDIS_TOKEN}"}
    try:
        response = requests.get(f"{REDIS_URL}/get/test_connection", headers=headers)
        if response.status_code == 200:
            print("[SUCCESS] Upstash Redis Connection Successful!")
        else:
            print(f"[FAILED] Upstash Redis Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[FAILED] Upstash Redis Exception: {e}")

def test_vector():
    print("\nTesting Upstash Vector...")
    # Using Vector REST API: /info
    headers = {"Authorization": f"Bearer {VECTOR_TOKEN}"}
    try:
        response = requests.get(f"{VECTOR_URL}/info", headers=headers)
        if response.status_code == 200:
            print("[SUCCESS] Upstash Vector Connection Successful!")
            print(f"   Info: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"[FAILED] Upstash Vector Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[FAILED] Upstash Vector Exception: {e}")

def test_qstash():
    print("\nTesting Upstash QStash (Workflow)...")
    # Using QStash REST API: /v2/keys
    headers = {"Authorization": f"Bearer {QSTASH_TOKEN}"}
    try:
        response = requests.get(f"{QSTASH_URL}/v2/keys", headers=headers)
        if response.status_code == 200:
            print("[SUCCESS] Upstash QStash Connection Successful!")
        else:
            print(f"[FAILED] Upstash QStash Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[FAILED] Upstash QStash Exception: {e}")

if __name__ == "__main__":
    print("====================================")
    print("   Testing Upstash Infrastructure   ")
    print("====================================\n")
    test_redis()
    test_vector()
    test_qstash()
    print("\n====================================")
