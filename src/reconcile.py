"""
Payment Platform Reconciliation & Discrepancy Engine
Description:
    Automated batch engine that performs cross-system reconciliation
    between internal gateway transaction logs and external merchant settlement records.
"""

import json
from decimal import Decimal

# Simulated Internal Gateway Ledger
INTERNAL_GATEWAY_DB = [
    {"transaction_id": "TXN-20261001-001", "merchant_id": "MCH-001", "amount": Decimal("150000.00"), "status": "SUCCESS"},
    {"transaction_id": "TXN-20261001-002", "merchant_id": "MCH-001", "amount": Decimal("499000.00"), "status": "SUCCESS"},
    {"transaction_id": "TXN-20261001-003", "merchant_id": "MCH-002", "amount": Decimal("75000.00"),  "status": "TIMEOUT"},
    {"transaction_id": "TXN-20261001-004", "merchant_id": "MCH-003", "amount": Decimal("1200000.00"), "status": "SUCCESS"},
    {"transaction_id": "TXN-20261001-005", "merchant_id": "MCH-001", "amount": Decimal("320000.00"), "status": "FAILED"},
]

# Simulated External Merchant Settlement Batch Report
EXTERNAL_MERCHANT_FEED = [
    {"transaction_id": "TXN-20261001-001", "merchant_id": "MCH-001", "amount": Decimal("150000.00"), "status": "SUCCESS"},
    {"transaction_id": "TXN-20261001-002", "merchant_id": "MCH-001", "amount": Decimal("490000.00"), "status": "SUCCESS"},
    {"transaction_id": "TXN-20261001-003", "merchant_id": "MCH-002", "amount": Decimal("75000.00"),  "status": "SUCCESS"},
    {"transaction_id": "TXN-20261001-006", "merchant_id": "MCH-002", "amount": Decimal("210000.00"), "status": "SUCCESS"},
]

class ReconciliationEngine:
    def __init__(self, internal_ledger, external_feed):
        self.internal = {item["transaction_id"]: item for item in internal_ledger}
        self.external = {item["transaction_id"]: item for item in external_feed}
        self.results = []

    def run_audit(self):
        all_ids = set(self.internal.keys()).union(set(self.external.keys()))
        
        for txn_id in sorted(all_ids):
            in_record = self.internal.get(txn_id)
            ex_record = self.external.get(txn_id)

            if in_record and not ex_record:
                self.results.append({
                    "transaction_id": txn_id,
                    "match_status": "MISSING_IN_MERCHANT",
                    "gateway_amount": float(in_record["amount"]),
                    "merchant_amount": None,
                    "action_required": "Notify merchant of uncaptured settlement entry"
                })
            elif ex_record and not in_record:
                self.results.append({
                    "transaction_id": txn_id,
                    "match_status": "MISSING_IN_GATEWAY",
                    "gateway_amount": None,
                    "merchant_amount": float(ex_record["amount"]),
                    "action_required": "Investigate unrouted or orphaned transaction"
                })
            else:
                amount_match = in_record["amount"] == ex_record["amount"]
                status_match = in_record["status"] == ex_record["status"]

                if amount_match and status_match:
                    self.results.append({
                        "transaction_id": txn_id,
                        "match_status": "PERFECT_MATCH",
                        "gateway_amount": float(in_record["amount"]),
                        "merchant_amount": float(ex_record["amount"]),
                        "action_required": "Auto-cleared for payout"
                    })
                elif not amount_match:
                    self.results.append({
                        "transaction_id": txn_id,
                        "match_status": "DISCREPANCY_AMOUNT_MISMATCH",
                        "gateway_amount": float(in_record["amount"]),
                        "merchant_amount": float(ex_record["amount"]),
                        "action_required": f"Variance of {float(in_record['amount'] - ex_record['amount'])} detected"
                    })
                elif not status_match:
                    self.results.append({
                        "transaction_id": txn_id,
                        "match_status": "DISCREPANCY_STATUS_MISMATCH",
                        "gateway_amount": float(in_record["amount"]),
                        "merchant_amount": float(ex_record["amount"]),
                        "action_required": f"Gateway ({in_record['status']}) != Merchant ({ex_record['status']})"
                    })

        return self.results

if __name__ == "__main__":
    engine = ReconciliationEngine(INTERNAL_GATEWAY_DB, EXTERNAL_MERCHANT_FEED)
    audit_summary = engine.run_audit()
    print("Reconciliation Audit Run Completed:")
    print(json.dumps(audit_summary, indent=2))
