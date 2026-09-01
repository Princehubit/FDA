CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(50) PRIMARY KEY,
    card_id VARCHAR(50) UNIQUE NOT NULL,
    avg_ticket_amount NUMERIC(10, 2) DEFAULT 500.00,
    primary_merchant_category VARCHAR(50) DEFAULT 'GROCERY',
    risk_profile VARCHAR(20) DEFAULT 'LOW'
);

CREATE TABLE IF NOT EXISTS transactions (
    txn_id VARCHAR(64) PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    card_id VARCHAR(50) NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    merchant_category VARCHAR(50) NOT NULL,
    reconstruction_loss NUMERIC(6, 4) NOT NULL,
    decision VARCHAR(20) NOT NULL,
    pos_entry_mode VARCHAR(30) DEFAULT 'NFC_CONTACTLESS'
);