"""Unit tests for standalone verification CLI and bundle format."""
import json
import base64
import pytest
from pathlib import Path

from scripts.verify_review_artifact import verify_bundle
from qsmlops.crypto.hashing import digest_document, sha3_hex
from qsmlops.crypto.providers import SIGNATURE_PROVIDERS


def test_verify_bundle_success_and_tamper_detection(tmp_path):
    provider = SIGNATURE_PROVIDERS["ML-DSA-65"]
    keypair = provider.generate_keypair()

    canonical_doc = {
        "format_version": "closure_trace_canonical/1.0.0",
        "entity_id": "ent_test",
        "run_id": "run_test",
        "decision": {
            "action": "confirm",
            "reason": "Verified execution gap on critical alert.",
        },
    }
    digest = digest_document(canonical_doc)
    sig = provider.sign(keypair.secret_key, digest.encode("utf-8"))
    pub_fingerprint = sha3_hex(keypair.public_key)

    bundle = {
        "format_version": "closure_trace_bundle/1.0.0",
        "run_id": "run_test",
        "organization_id": "org_test",
        "canonical_document": canonical_doc,
        "canonical_digest": digest,
        "receipt": {
            "id": "rec_test",
            "algorithm_id": "ML-DSA-65",
            "public_key_b64": base64.b64encode(keypair.public_key).decode("ascii"),
            "public_key_fingerprint": pub_fingerprint,
            "signature_b64": base64.b64encode(sig).decode("ascii"),
            "created_at": 1000.0,
        },
        "ledger": {
            "entry_hash": "ledger_entry_hash_12345",
        },
    }

    # 1. Genuine bundle verifies
    ok, msgs = verify_bundle(bundle, expected_key_fingerprint=pub_fingerprint)
    assert ok is True

    # 2. Tampered canonical document is caught
    tampered_doc_bundle = json.loads(json.dumps(bundle))
    tampered_doc_bundle["canonical_document"]["decision"]["action"] = "dismiss"
    ok, msgs = verify_bundle(tampered_doc_bundle)
    assert ok is False
    assert any("Digest mismatch" in m for m in msgs)

    # 3. Tampered signature is caught
    tampered_sig_bundle = json.loads(json.dumps(bundle))
    tampered_sig_bundle["receipt"]["signature_b64"] = base64.b64encode(b"invalid_signature_bytes" * 100).decode("ascii")
    ok, msgs = verify_bundle(tampered_sig_bundle)
    assert ok is False
    assert any("signature verification failed" in m for m in msgs)
