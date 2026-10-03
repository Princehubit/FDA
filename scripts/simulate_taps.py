import time
import uuid
import random
import requests

# Point to your Android Edge Server
SERVER_URL = "http://10.196.27.129:8000/api/v1/score-transaction"

CATEGORIES = ["GROCERY", "DINING", "ELECTRONICS", "LUXURY_JEWELRY"]

def generate_tap():
    category = random.choices(CATEGORIES, weights=[0.5, 0.3, 0.15, 0.05])[0]
    
    # Generate realistic amounts based on category
    if category == "GROCERY":
        amount = round(random.uniform(50.0, 1500.0), 2)
    elif category == "DINING":
        amount = round(random.uniform(200.0, 3500.0), 2)
    elif category == "ELECTRONICS":
        amount = round(random.uniform(2500.0, 45000.0), 2)
    else:
        amount = round(random.uniform(50000.0, 120000.0), 2)

    return {
        "txn_id": f"TXN_{str(uuid.uuid4())[:8].upper()}",
        "card_id": f"CARD_{random.randint(100, 999)}",
        "user_id": f"USR_{random.randint(1, 20)}",
        "amount": amount,
        "merchant_category": category,
        "pos_entry_mode": "NFC_CONTACTLESS"
    }

def main():
    print(f"[*] Starting tap stream targeting {SERVER_URL}...")
    while True:
        payload = generate_tap()
        try:
            start = time.time()
            resp = requests.post(SERVER_URL, json=payload, timeout=5)
            latency = round((time.time() - start) * 1000, 2)

            if resp.status_code == 200:
                data = resp.json()
                print(f"[{data['decision']}] Txn: {data['txn_id']} | Loss: {data['reconstruction_loss']} | Latency: {latency}ms")
            else:
                print(f"[ERROR] HTTP {resp.status_code}: {resp.text}")
        except Excepwtion as e:
            print(f"[CONN ERROR] {e}")

        time.sleep(1.5)

if __name__ == "__main__":
    main()