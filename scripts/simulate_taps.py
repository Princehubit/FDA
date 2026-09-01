import time
import requests
import random
import uuid

API_URL = "http://localhost:8000/api/v1/score-transaction"

# Pre-configured test profiles (matching seeded users)
PROFILES = [
    {"user_id": "USR_9101_STD", "card_id": "CRD_IN_101_NORM", "category": "GROCERY", "base_amount": (150.0, 900.0)},
    {"user_id": "USR_9202_VEL", "card_id": "CRD_IN_202_ANOM", "category": "DINING", "base_amount": (800.0, 2500.0)},
    {"user_id": "USR_9303_RISK", "card_id": "CRD_IN_303_FRAUD", "category": "LUXURY_JEWELRY", "base_amount": (45000.0, 120000.0)},
]

def generate_mock_tap():
    # 70% normal transactions, 20% high amounts / fraud, 10% velocity stress
    event_type = random.choices(["NORMAL", "FRAUD", "VELOCITY_SPIKE"], weights=[0.7, 0.2, 0.1])[0]

    if event_type == "NORMAL":
        profile = PROFILES[0]
        amount = round(random.uniform(*profile["base_amount"]), 2)
        category = "GROCERY"
    elif event_type == "FRAUD":
        profile = PROFILES[2]
        amount = round(random.uniform(*profile["base_amount"]), 2)
        category = "LUXURY_JEWELRY"
    else:  # VELOCITY_SPIKE
        profile = PROFILES[1]
        amount = round(random.uniform(2000.0, 6000.0), 2)
        category = "ELECTRONICS"

    payload = {
        "txn_id": f"TXN_{uuid.uuid4().hex[:8].upper()}",
        "card_id": profile["card_id"],
        "user_id": profile["user_id"],
        "amount": amount,
        "merchant_category": category,
        "pos_entry_mode": "NFC_CONTACTLESS"
    }

    try:
        res = requests.post(API_URL, json=payload)
        data = res.json()
        print(f"[{payload['txn_id']}] Card: {payload['card_id']} | ₹{payload['amount']:>8.2f} | Category: {payload['merchant_category']:<14} -> Decision: {data.get('decision')} (Loss: {data.get('reconstruction_loss')})")
    except Exception as e:
        print(f"[!] Error sending tap to API: {e}")

if __name__ == "__main__":
    print("=" * 70)
    print("Starting Mock NFC Edge Tap Stream (Press Ctrl+C to stop)")
    print("=" * 70)
    
    while True:
        generate_mock_tap()
        time.sleep(random.uniform(1.5, 3.5))  # Simulates realistic physical tap intervals