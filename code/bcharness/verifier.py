"""Point-of-action clearance verifier implementing the five BC controls:
 1 payload-bound (payment_id, amount, currency, payee, validity window)
 2 signed by the checker (signature verifies against a registered key)
 3 verified at the point of action (called by the executing service, see bank.py)
 4 fail closed (anything missing or unverifiable -> refuse)
 5 signer entitled to clear this payload (check type + amount limit)
plus one-time use (nonce) to stop replay."""
from dataclasses import dataclass, field
from . import crypto

REQUIRED_FIELDS = ("payment_id", "amount", "currency", "payee_iban", "check", "valid_from", "valid_until", "nonce", "signer")


@dataclass
class Signer:
    signer_id: str
    pub: str
    entitled_checks: tuple
    amount_limit: float


@dataclass
class Registry:
    signers: dict = field(default_factory=dict)
    used_nonces: set = field(default_factory=set)

    def add(self, s: Signer):
        self.signers[s.signer_id] = s


def verify_clearance(token, payment: dict, now: int, registry: Registry, required_check="sanctions"):
    """Return (ok: bool, reason: str). Never raises on malformed input (fail closed)."""
    if not token or not isinstance(token, dict):
        return False, "no_clearance"
    payload, sig = token.get("payload"), token.get("sig")
    if not isinstance(payload, dict) or not isinstance(sig, str):
        return False, "malformed"
    missing = [f for f in REQUIRED_FIELDS if f not in payload]
    if missing:
        return False, "not_payload_bound"            # control 1
    signer = registry.signers.get(payload["signer"])
    if signer is None:
        return False, "unknown_signer"               # control 2
    if not crypto.verify(signer.pub, payload, sig):
        return False, "bad_signature"                # control 2
    for f_tok, f_pay in (("payment_id", "payment_id"), ("amount", "amount"), ("currency", "currency"), ("payee_iban", "payee_iban")):
        if payload[f_tok] != payment[f_pay]:
            return False, "payload_mismatch"         # control 1
    if payload["check"] != required_check:
        return False, "wrong_check"
    if not (payload["valid_from"] <= now <= payload["valid_until"]):
        return False, "expired"                      # control 1 (window)
    if payload["nonce"] in registry.used_nonces:
        return False, "replayed"
    if required_check not in signer.entitled_checks or payment["amount"] > signer.amount_limit:
        return False, "signer_not_entitled"          # control 5
    return True, "valid"
