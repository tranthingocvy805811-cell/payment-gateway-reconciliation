-- ============================================================================
-- Payment Platform Core & Automated Reconciliation Schema
-- ============================================================================

DROP TABLE IF EXISTS reconciliation_results;
DROP TABLE IF EXISTS merchant_settlement_logs;
DROP TABLE IF EXISTS transactions;

-- 1. Internal Core Gateway Transactions Ledger
CREATE TABLE transactions (
    transaction_id VARCHAR(64) PRIMARY KEY,
    order_id VARCHAR(64) NOT NULL,
    merchant_id VARCHAR(32) NOT NULL,
    user_id VARCHAR(32) NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'VND',
    payment_method VARCHAR(32) NOT NULL, -- QR_CODE, DOMESTIC_CARD, WALLET_BALANCE
    status VARCHAR(20) NOT NULL,         -- SUCCESS, FAILED, TIMEOUT, PENDING
    error_code VARCHAR(32),              -- None, ERR_GATEWAY_TIMEOUT, ERR_INSUFFICIENT_FUNDS
    idempotency_key VARCHAR(128) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. External Merchant Settlement Log (Ingested daily)
CREATE TABLE merchant_settlement_logs (
    record_id VARCHAR(64) PRIMARY KEY,
    merchant_id VARCHAR(32) NOT NULL,
    transaction_id VARCHAR(64) NOT NULL,
    order_id VARCHAR(64) NOT NULL,
    reported_amount DECIMAL(15, 2) NOT NULL,
    reported_status VARCHAR(20) NOT NULL, -- SUCCESS, FAILED
    settled_at TIMESTAMP NOT NULL
);

-- 3. Audit & Reconciliation Results
CREATE TABLE reconciliation_results (
    audit_id SERIAL PRIMARY KEY,
    reconciled_date DATE NOT NULL,
    transaction_id VARCHAR(64),
    merchant_id VARCHAR(32),
    match_status VARCHAR(30) NOT NULL, -- MATCHED, AMOUNT_MISMATCH, STATUS_MISMATCH, MISSING_IN_GATEWAY, MISSING_IN_MERCHANT
    gateway_amount DECIMAL(15, 2),
    merchant_amount DECIMAL(15, 2),
    discrepancy_note TEXT,
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_trans_merchant ON transactions(merchant_id, created_at);
CREATE INDEX idx_audit_date ON reconciliation_results(reconciled_date, match_status);
