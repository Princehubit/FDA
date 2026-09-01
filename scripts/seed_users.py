import psycopg2
import redis

# 1. Connect and initialize PostgreSQL records
try:
    conn = psycopg2.connect(
        host="localhost", database="fraud_db", user="postgres", password="postgrespassword", port=5432
    )
    profiles = [
        ("USR_9101_STD", "CRD_IN_101_NORM", 800.00, "GROCERY", "LOW"),
        ("USR_9202_VEL", "CRD_IN_202_ANOM", 4500.00, "ELECTRONICS", "MEDIUM"),
        ("USR_9303_RISK", "CRD_IN_303_FRAUD", 75000.00, "LUXURY_JEWELRY", "HIGH")
    ]

    with conn.cursor() as cur:
        for u_id, c_id, avg_amt, cat, risk in profiles:
            cur.execute("""
                INSERT INTO users (user_id, card_id, avg_ticket_amount, primary_merchant_category, risk_profile)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (user_id) DO NOTHING;
            """, (u_id, c_id, avg_amt, cat, risk))
        conn.commit()
    conn.close()
    print("[+] PostgreSQL users seeded successfully.")
except Exception as e:
    print(f"[!] PostgreSQL seeding skipped: {e}")

# 2. Flush Redis velocity counters
try:
    r = redis.Redis(host="localhost", port=6379, db=0)
    r.flushdb()
    print("[+] Redis cache reset successfully.")
except Exception as e:
    print(f"[!] Redis reset skipped: {e}")