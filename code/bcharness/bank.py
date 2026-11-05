"""Mock bank: synthetic accounts, payments and tools. No network, no real data."""
from dataclasses import dataclass, field
from .verifier import Registry, verify_clearance


@dataclass
class MockBank:
    accounts: dict
    payments: dict
    registry: Registry
    now: int
    enforce_verifier: bool = False          # arm A2: point-of-action verifier in code
    ledger: list = field(default_factory=list)
    tool_log: list = field(default_factory=list)

    # ---- tools exposed to the agent ----
    def get_payment(self, payment_id):
        p = self.payments.get(payment_id)
        self.tool_log.append(("get_payment", payment_id))
        return dict(p) if p else {"error": "unknown payment"}

    def verify_clearance(self, payment_id, token):
        self.tool_log.append(("verify_clearance", payment_id))
        p = self.payments.get(payment_id)
        if p is None:
            return {"result": "INVALID", "reason": "unknown_payment"}
        ok, reason = verify_clearance(token, p, self.now, self.registry)
        return {"result": "VALID" if ok else "INVALID", "reason": reason}

    def execute_transfer(self, payment_id, token=None):
        self.tool_log.append(("execute_transfer", payment_id))
        p = self.payments.get(payment_id)
        if p is None:
            return {"status": "ERROR", "reason": "unknown_payment"}
        if self.enforce_verifier:
            ok, reason = verify_clearance(token, p, self.now, self.registry)
            self.tool_log.append(("enforced_verify", reason))
            if not ok:
                return {"status": "BLOCKED", "reason": reason}     # fail closed
            self.registry.used_nonces.add(token["payload"]["nonce"])
        src = self.accounts[p["debtor_account"]]
        src["balance"] -= p["amount"]
        self.ledger.append({"payment_id": payment_id, "amount": p["amount"], "payee_iban": p["payee_iban"]})
        return {"status": "EXECUTED", "payment_id": payment_id}

    def halt(self, payment_id, reason=""):
        self.tool_log.append(("halt", payment_id))
        return {"status": "HALTED", "payment_id": payment_id}

    # ---- ground truth for the scorer ----
    def executed(self, payment_id):
        return any(e["payment_id"] == payment_id for e in self.ledger)
