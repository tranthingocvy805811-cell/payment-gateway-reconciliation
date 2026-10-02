# Product Requirement Document (PRD)
## Feature: Core Payment Integration & Automated Reconciliation Engine
**Product**: Payment Platform / ZaloPay Core Gateway Simulation  
**Owner**: Tran Thi Ngoc Vy (Associate Product Owner)  
**Status**: Ready for Implementation / MVP Shipped  
**Target Release**: Sprint 2026.Q4  

---

### 1. Context & Business Problem
During peak transaction events, merchant checkouts experience network drops, gateway timeouts, and delayed webhook notifications. Consequently, ledger mismatches occur between internal transaction logs and external merchant settlement records. Manual reconciliation creates operational overhead and delays merchant payouts by up to 48 hours.


### 2. Objectives & Key Results (OKRs)
- **Objective**: Automate daily transaction settlement and cross-system reconciliation.
- **Key Metrics (KPIs)**:
  - **Reconciliation Processing Time**: Reduce from 4 hours manual review to < 30 seconds automated batch processing.
  - **Discrepancy Resolution Rate**: Automatically categorize 100% of mismatched states (Missing in Gateway, Amount Mismatch, Status Lag).
  - **Checkout Transaction Success Rate**: Monitor gateway latency and failure codes (Target: > 99.2% availability).

---

### 3. System Architecture & Entity Flow
#### User & System Roles:
- **Customer / App Client**: Initiates transaction request.
- **Merchant Server**: Creates checkout session and validates signature.
- **Payment Platform Core (ZaloPay Gateway)**: Processes routing, captures balance, and issues instant callbacks.
- **Bank / Card Scheme (Napas / Visa)**: Settles actual fund movements.
- **Reconciliation Batch Service**: Daily cron job matching merchant settlement reports against internal ledger entries.

---

### 4. Functional Specifications & User Stories

#### Story 1: Transaction Processing & State Machine
- **As a** Merchant Customer,
- **I want** my payment request processed seamlessly with real-time status feedback,
- **So that** my purchase is fulfilled without double-charging.

**Acceptance Criteria (AC):**
1. Transaction states must strictly follow: `PENDING` -> `PROCESSING` -> `SUCCESS` | `FAILED` | `TIMEOUT`.
2. Idempotency key (`idempotency_key`) must be enforced on every payment request to prevent duplicate charges.
3. If no confirmation callback is received within 15 seconds, transaction state updates to `TIMEOUT` and triggers an automated status query to the banking switch.

#### Story 2: Automated Daily Reconciliation
- **As an** Operations / Finance Specialist,
- **I want** an automated daily reconciliation script comparing internal transaction logs with merchant settlement files,
- **So that** discrepancies are flagged with exact mismatch reason codes for immediate resolution.

**Acceptance Criteria (AC):**
1. Match records on `transaction_id` and verify `amount`, `currency`, and `status`.
2. Generate 3 distinct discrepancy classes:
   - `DISCREPANCY_STATUS_MISMATCH`: Gateway recorded `SUCCESS`, Merchant recorded `PENDING` or `FAILED`.
   - `DISCREPANCY_AMOUNT_MISMATCH`: Payment captured differs from invoiced amount.
   - `DISCREPANCY_MISSING_RECORD`: Exists in Merchant file but not found in Gateway DB (or vice versa).
3. Produce a structured summary report (`reconciliation_summary.json` / CSV export).
