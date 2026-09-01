from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import torch
import redis
import psycopg2
from datetime import datetime
import os
from app.schemas import TapPayload
from src.models.autoencoder import FraudAutoencoder

app = FastAPI(title="NFC Edge Fraud Detection Engine")

# CORS setup for mobile and web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = FraudAutoencoder(input_dim=5).to(device)

model_path = os.path.join("src", "models", "autoencoder_rtx.pt")
if os.path.exists(model_path):
    model.load_state_dict(torch.load(model_path, map_location=device))
    print(f"[*] Loaded trained model from {model_path} onto {device}")
model.eval()

# Redis connection
r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

def get_db():
    return psycopg2.connect(
        host="localhost",
        database="fraud_db",
        user="postgres",
        password="prince!71@post",
        port=5432
    )

CATEGORY_MAP = {"GROCERY": 0.1, "DINING": 0.3, "ELECTRONICS": 0.7, "LUXURY_JEWELRY": 0.95}

@app.get("/")
def health_check():
    return {"status": "online", "device": str(device), "service": "NFC Fraud Guard Engine"}

@app.post("/api/v1/score-transaction")
def score_transaction(payload: TapPayload):
    try:
        # 1. Sliding window velocity tracking via Redis
        vel_key = f"vel:{payload.card_id}"
        velocity = 1
        try:
            velocity = r.incr(vel_key)
            if velocity == 1:
                r.expire(vel_key, 60)
        except Exception:
            velocity = 1  # Fallback if Redis is idle

        # 2. Vectorize input features
        hour_norm = datetime.now().hour / 24.0
        cat_val = CATEGORY_MAP.get(payload.merchant_category.upper(), 0.5)
        amount_norm = min(payload.amount / 100000.0, 1.0)
        vel_norm = min(velocity / 5.0, 1.0)
        pos_norm = 0.2 if payload.pos_entry_mode == "NFC_CONTACTLESS" else 0.8

        input_vector = torch.tensor(
            [[amount_norm, cat_val, vel_norm, hour_norm, pos_norm]],
            dtype=torch.float32,
            device=device
        )

        # 3. Model reconstruction inference
        with torch.inference_mode():
            reconstruction = model(input_vector)
            loss = torch.mean((input_vector - reconstruction) ** 2).item()

        # 4. Multi-threshold decision logic
        if loss < 0.25 and velocity <= 2:
            decision = "APPROVE"
        elif loss < 0.70 or velocity <= 4:
            decision = "CHALLENGE"
        else:
            decision = "DECLINE"

        # 5. Persist transaction record
        try:
            conn = get_db()
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO transactions (txn_id, card_id, user_id, amount, merchant_category, reconstruction_loss, decision, pos_entry_mode)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                """, (payload.txn_id, payload.card_id, payload.user_id, payload.amount, payload.merchant_category, loss, decision, payload.pos_entry_mode))
                conn.commit()
            conn.close()
        except Exception as db_err:
            print(f"[!] DB Log skipped: {db_err}")

        return {
            "txn_id": payload.txn_id,
            "decision": decision,
            "reconstruction_loss": round(loss, 4),
            "velocity_count": velocity,
            "device": str(device)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))