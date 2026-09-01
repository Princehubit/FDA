import psycopg2

def insert_test_data():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="fraud_db",
            user="postgres",
            password="prince!71@post",
            port=5432
        )
        cur = conn.cursor()

        sample_transactions = [
            ('TXN_INIT_001', 'CRD_IN_101_NORM', 'USR_9101_STD', 450.00, 'GROCERY', 0.0821, 'APPROVE', 'NFC_CONTACTLESS'),
            ('TXN_INIT_002', 'CRD_IN_303_FRAUD', 'USR_9303_RISK', 85000.00, 'LUXURY_JEWELRY', 0.8924, 'DECLINE', 'NFC_CONTACTLESS'),
            ('TXN_INIT_003', 'CRD_IN_202_ANOM', 'USR_9202_VEL', 3500.00, 'DINING', 0.4120, 'CHALLENGE', 'NFC_CONTACTLESS'),
            ('TXN_INIT_004', 'CRD_IN_101_NORM', 'USR_9101_STD', 820.50, 'GROCERY', 0.1105, 'APPROVE', 'NFC_CONTACTLESS'),
            ('TXN_INIT_005', 'CRD_IN_303_FRAUD', 'USR_9303_RISK', 92000.00, 'LUXURY_JEWELRY', 0.9410, 'DECLINE', 'NFC_CONTACTLESS')
        ]

        for txn in sample_transactions:
            cur.execute("""
                INSERT INTO transactions (txn_id, card_id, user_id, amount, merchant_category, reconstruction_loss, decision, pos_entry_mode)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (txn_id) DO NOTHING;
            """, txn)

        conn.commit()
        cur.close()
        conn.close()
        print("[+] Successfully inserted sample transactions into PostgreSQL!")

    except Exception as e:
        print(f"[!] Database error: {e}")

if __name__ == "__main__":
    insert_test_data()