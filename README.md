# Payment Gateway Integration & Automated Reconciliation Engine

An end-to-end Technical Product Specification & Reconciliation Engine simulating core payment transaction processing, asynchronous webhook handling, and daily ledger reconciliation between merchant settlement files and internal gateway ledgers.

---

## 📌 Project Overview
- **Role**: Associate Product Owner (Technical Platform)
- **Domain**: Payment Core Infrastructure & Financial Reconciliation
- **Stack**: Python 3.10+, PostgreSQL / SQLite, Mermaid UML, Git

This project demonstrates the core responsibilities of a Platform Product Owner at a Fintech company (e.g., ZaloPay):
1. **Product Requirement Document (PRD)** defining the transaction lifecycle state machine, idempotency key enforcement, and edge case handling.
2. **UML Sequence Diagram** illustrating asynchronous 3-party checkout interactions (Client, Merchant, Payment Gateway, Banking Switch).
3. **Relational Database Schema (`schema.sql`)** modeling core transactional logs and audit tables.
4. **Reconciliation Engine (`reconcile.py`)** automatically identifying, flagging, and categorizing 100% of amount & status mismatches.

---

## 🏛️ System Architecture & Sequence Flow

```mermaid
sequenceDiagram
    autonumber
    actor Customer as User / App
    participant Merchant as Merchant Backend
    participant Gateway as Payment Platform (ZaloPay)
    participant Bank as Core Banking / Switch

    Customer->>Merchant: 1. Checkout Order (Item, Total)
    Merchant->>Gateway: 2. POST /v2/payments/create (Order Info, Idempotency-Key)
    Gateway-->>Merchant: 3. Return Payment URL / QR Code
    Merchant-->>Customer: 4. Display QR / Redirect to Payment
    Customer->>Gateway: 5. Authorize & Confirm Payment (PIN / Biometrics)
    Gateway->>Bank: 6. Request Debit / Fund Movement
    Bank-->>Gateway: 7. Debit Confirmed (SUCCESS)
    Gateway->>Gateway: 8. Update Transaction State = SUCCESS
    Gateway-->>Merchant: 9. Asynchronous Webhook Callback (Status: SUCCESS)
    Merchant-->>Gateway: 10. HTTP 200 OK (Acknowledged)
    Merchant-->>Customer: 11. Display Order Success Page
```

---

## 📊 Automated Reconciliation Logic

The daily reconciliation script compares **Internal Gateway Ledgers** against **Merchant Settlement Reports** to identify financial discrepancies:

```mermaid
flowchart TD
    A[Daily Batch Trigger] --> B[Ingest Internal Gateway Ledger]
    A --> C[Ingest External Merchant Batch]
    B & C --> D{Compare on Transaction ID}
    D -->|Match & Amounts Equal| E[✅ Status: PERFECT_MATCH -> Auto Cleared]
    D -->|Amount Mismatch| F[⚠️ Flag: DISCREPANCY_AMOUNT_MISMATCH]
    D -->|Status Mismatch| G[⚠️ Flag: DISCREPANCY_STATUS_MISMATCH]
    D -->|Missing in Gateway| H[❌ Flag: MISSING_IN_GATEWAY]
    D -->|Missing in Merchant| I[❌ Flag: MISSING_IN_MERCHANT]
    E & F & G & H & I --> J[Output Audit Report JSON / DB Log]
```

---

## 🚀 How to Run the Prototype

1. **Clone the repository**:
   ```bash
   git clone [https://github.com/tranthingocvy805811-cell/payment-gateway-reconciliation.git](https://github.com/tranthingocvy805811-cell/payment-gateway-reconciliation.git)
   cd payment-gateway-reconciliation
   ```

2. **Execute the Reconciliation Engine**:
   ```bash
   python src/reconcile.py
   ```

---

## 📂 Repository Structure
```text
├── docs/
│   └── PRD_Payment_Platform.md     # Detailed functional specifications & user stories
├── sql/
│   └── schema.sql                  # Database DDL with indexes and audit tables
├── src/
│   └── reconcile.py                # Automated discrepancy matching script
└── README.md                       # Architecture, sequence diagrams & execution guide
```
