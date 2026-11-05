"""Ed25519 signing of clearance payloads (canonical JSON). Keys are generated per draw from a seed,
so runs are reproducible and no real key material exists anywhere."""
import base64, hashlib, json
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature


def canonical(payload: dict) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()


def key_from_seed(label: str, seed: int) -> Ed25519PrivateKey:
    raw = hashlib.sha256(f"bc-harness|{label}|{seed}".encode()).digest()
    return Ed25519PrivateKey.from_private_bytes(raw)


def pub_b64(key: Ed25519PrivateKey) -> str:
    pk = key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    return base64.b64encode(pk).decode()


def sign(key: Ed25519PrivateKey, payload: dict) -> str:
    return base64.b64encode(key.sign(canonical(payload))).decode()


def verify(pub: str, payload: dict, sig: str) -> bool:
    try:
        Ed25519PublicKey.from_public_bytes(base64.b64decode(pub)).verify(base64.b64decode(sig), canonical(payload))
        return True
    except (InvalidSignature, ValueError):
        return False
