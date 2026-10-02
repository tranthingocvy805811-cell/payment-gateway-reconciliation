import streamlit as st
import pandas as pd
from decimal import Decimal
import plotly.express as px

st.set_page_config(
    page_title="Payment Gateway & Reconciliation Engine",
    page_icon="💳",
    layout="wide"
)

st.title("💳 Payment Gateway Core & Automated Reconciliation Platform")
st.caption("A Technical Product Demonstration by **Tran Thi Ngoc Vy** | Target: Associate Product Owner, Zalopay")

# Tab Navigation
tab_overview, tab_flow, tab_recon, tab_prd = st.tabs([
    "📊 Executive Metrics", 
    "🔄 Architecture & Sequence Flow", 
    "⚙️ Live Reconciliation Engine", 
    "📑 PRD & Specifications"
])

# Simulated Data
gateway_data = [
    {"transaction_id": "TXN-20261001-001", "merchant_id": "MCH-SHOPEE", "amount": 150000.0, "status": "SUCCESS", "method": "QR_CODE", "timestamp": "2026-10-01 10:14:22"},
    {"transaction_id": "TXN-20261001-002", "merchant_id": "MCH-TIKI", "amount": 499000.0, "status": "SUCCESS", "method": "DOMESTIC_CARD", "timestamp": "2026-10-01 10:15:05"},
    {"transaction_id": "TXN-20261001-003", "merchant_id": "MCH-GRAB", "amount": 75000.0, "status": "TIMEOUT", "method": "WALLET_BALANCE", "timestamp": "2026-10-01 10:16:30"},
    {"transaction_id": "TXN-20261001-004", "merchant_id": "MCH-BAEMIN", "amount": 1200000.0, "status": "SUCCESS", "method": "DOMESTIC_CARD", "timestamp": "2026-10-01 10:18:11"},
    {"transaction_id": "TXN-20261001-005", "merchant_id": "MCH-SHOPEE", "amount": 320000.0, "status": "FAILED", "method": "QR_CODE", "timestamp": "2026-10-01 10:20:45"},
]

merchant_data = [
    {"transaction_id": "TXN-20261001-001", "merchant_id": "MCH-SHOPEE", "amount": 150000.0, "status": "SUCCESS"},
    {"transaction_id": "TXN-20261001-002", "merchant_id": "MCH-TIKI", "amount": 490000.0, "status": "SUCCESS"}, # Lệch tiền
    {"transaction_id": "TXN-20261001-003", "merchant_id": "MCH-GRAB", "amount": 75000.0, "status": "SUCCESS"},   # Lệch trạng thái
    {"transaction_id": "TXN-20261001-006", "merchant_id": "MCH-GRAB", "amount": 210000.0, "status": "SUCCESS"},  # Thiếu ở Gateway
]

with tab_overview:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Volume Processed", "2,244,000 VND", "+18.4% WoW")
    col2.metric("Gateway Success Rate", "80.0%", "Target > 99.2%")
    col3.metric("Avg Latency", "342 ms", "-45 ms")
    col4.metric("Discrepancies Flagged", "3 Cases", "Auto Detected")
    
    st.markdown("---")
    st.subheader("Real-Time Gateway Transaction Ledger")
    df_gw = pd.DataFrame(gateway_data)
    st.dataframe(df_gw, use_container_width=True)

with tab_flow:
    st.subheader("Core 3-Way Asynchronous Checkout Flow")
    st.markdown('''
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
    ''')
    st.info("💡 **Platform PO Insight**: Idempotency keys prevent duplicate debits during unstable mobile connections.")

with tab_recon:
    st.subheader("Daily Ledger Reconciliation & Audit Engine")
    st.write("Compare internal gateway records against external settlement files to auto-flag variances.")
    
    if st.button("🚀 Run Automated Audit Engine"):
        gw_dict = {x["transaction_id"]: x for x in gateway_data}
        mc_dict = {x["transaction_id"]: x for x in merchant_data}
        all_ids = set(gw_dict.keys()).union(set(mc_dict.keys()))
        
        audit_results = []
        for tid in sorted(all_ids):
            gw = gw_dict.get(tid)
            mc = mc_dict.get(tid)
            if gw and not mc:
                audit_results.append({"Transaction ID": tid, "Match Status": "MISSING_IN_MERCHANT", "Gateway Amt": f"{gw['amount']:,.0f}", "Merchant Amt": "N/A", "Severity": "HIGH", "Resolution": "Notify merchant of uncaptured batch entry"})
            elif mc and not gw:
                audit_results.append({"Transaction ID": tid, "Match Status": "MISSING_IN_GATEWAY", "Gateway Amt": "N/A", "Merchant Amt": f"{mc['amount']:,.0f}", "Severity": "CRITICAL", "Resolution": "Trace unrouted transaction logs"})
            else:
                amt_match = gw["amount"] == mc["amount"]
                st_match = gw["status"] == mc["status"]
                if amt_match and st_match:
                    audit_results.append({"Transaction ID": tid, "Match Status": "PERFECT_MATCH", "Gateway Amt": f"{gw['amount']:,.0f}", "Merchant Amt": f"{mc['amount']:,.0f}", "Severity": "NONE", "Resolution": "Auto-cleared for payout"})
                elif not amt_match:
                    diff = gw["amount"] - mc["amount"]
                    audit_results.append({"Transaction ID": tid, "Match Status": "AMOUNT_MISMATCH", "Gateway Amt": f"{gw['amount']:,.0f}", "Merchant Amt": f"{mc['amount']:,.0f}", "Severity": "HIGH", "Resolution": f"Variance of {diff:,.0f} VND flagged"})
                elif not st_match:
                    audit_results.append({"Transaction ID": tid, "Match Status": "STATUS_MISMATCH", "Gateway Amt": f"{gw['amount']:,.0f} ({gw['status']})", "Merchant Amt": f"{mc['amount']:,.0f} ({mc['status']})", "Severity": "MEDIUM", "Resolution": f"Gateway ({gw['status']}) != Merchant ({mc['status']})"})
        
        df_audit = pd.DataFrame(audit_results)
        st.success(f"Audit completed: {len(audit_results)} records processed.")
        st.dataframe(df_audit, use_container_width=True)

with tab_prd:
    st.subheader("Product Requirement Document (Summary)")
    st.markdown('''
    - **Target Release**: Sprint 2026.Q4
    - **Core Entities**: `transactions`, `merchant_settlement_logs`, `reconciliation_results`
    - **Failure Modes Handled**: Network Timeout, Idempotency Violations, Uncaptured Webhooks.
    ''')
