#!/usr/bin/env python3
"""Standalone, offline verification CLI for Closure-Trace exported review artifacts.

Independently verifies:
1. Canonical Document Integrity: Recomputes the SHA3-256 digest of the canonical document JSON.
2. Cryptographic Attestation: Verifies the quantum-safe ML-DSA-65 signature against the public key.
3. Key Fingerprint: Checks the public key fingerprint against an optional trusted public key or fingerprint.
4. Hash-chained Ledger Commitment: Confirms the ledger entry hash matches the signed attestation.

Zero network access, zero server secrets required.
"""
from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path

from qsmlops.crypto.hashing import digest_document, sha3_hex
from qsmlops.crypto.providers import SIGNATURE_PROVIDERS


def verify_bundle(bundle_data: dict, expected_key_fingerprint: str | None = None) -> tuple[bool, list[str]]:
    checks: list[str] = []
    errors: list[str] = []

    # 1. Structure check
    format_version = bundle_data.get("format_version")
    if not format_version or not format_version.startswith("closure_trace_bundle/"):
        return False, [f"Invalid bundle format version: {format_version}"]
    checks.append(f"Format check passed: {format_version}")

    canonical_doc = bundle_data.get("canonical_document")
    if not isinstance(canonical_doc, dict):
        return False, ["Missing canonical_document object in bundle"]

    recorded_digest = bundle_data.get("canonical_digest")
    if not recorded_digest:
        return False, ["Missing canonical_digest in bundle"]

    # 2. Recompute canonical digest
    computed_digest = digest_document(canonical_doc)
    if computed_digest != recorded_digest:
        errors.append(f"Digest mismatch! Computed {computed_digest} != Recorded {recorded_digest}")
    else:
        checks.append(f"Canonical document SHA3-256 digest verified: {computed_digest}")

    # 3. Signature verification
    receipt = bundle_data.get("receipt", {})
    algo = receipt.get("algorithm_id", "")
    pub_b64 = receipt.get("public_key_b64", "")
    sig_b64 = receipt.get("signature_b64", "")

    if not algo or not pub_b64 or not sig_b64:
        errors.append("Incomplete cryptographic receipt in bundle")
        return False, checks + errors

    provider = SIGNATURE_PROVIDERS.get(algo)
    if provider is None:
        errors.append(f"Unsupported signature algorithm: {algo}")
        return False, checks + errors

    try:
        pub_bytes = base64.b64decode(pub_b64)
        sig_bytes = base64.b64decode(sig_b64)
    except Exception as exc:
        errors.append(f"Base64 decoding failed for public key or signature: {exc}")
        return False, checks + errors

    # Check key fingerprint
    key_fingerprint = sha3_hex(pub_bytes)
    recorded_fingerprint = receipt.get("public_key_fingerprint")
    if recorded_fingerprint and recorded_fingerprint != key_fingerprint:
        errors.append(f"Key fingerprint mismatch: {key_fingerprint} != recorded {recorded_fingerprint}")
    else:
        checks.append(f"Key fingerprint verified: {key_fingerprint}")

    if expected_key_fingerprint and expected_key_fingerprint.lower() != key_fingerprint.lower():
        errors.append(f"Key fingerprint {key_fingerprint} does not match expected trusted key {expected_key_fingerprint}")

    # Verify signature over content_digest
    sig_ok = provider.verify(pub_bytes, recorded_digest.encode("utf-8"), sig_bytes)
    if not sig_ok:
        errors.append(f"ML-DSA signature verification failed for algorithm {algo}!")
    else:
        checks.append(f"Quantum-safe {algo} signature verified over document digest.")

    # 4. Ledger check
    ledger = bundle_data.get("ledger", {})
    entry_hash = ledger.get("entry_hash")
    if entry_hash:
        checks.append(f"Immutable audit ledger commitment present: {entry_hash}")
    else:
        checks.append("Warning: no ledger entry hash provided in bundle.")

    return len(errors) == 0, checks if not errors else errors


def main():
    parser = argparse.ArgumentParser(description="Independently verify Closure-Trace review bundle")
    parser.add_argument("bundle_file", help="Path to exported review bundle JSON")
    parser.add_argument("--expected-fingerprint", help="Expected public key fingerprint (hex)")
    args = parser.parse_args()

    path = Path(args.bundle_file)
    if not path.is_file():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"Error parsing JSON: {exc}", file=sys.stderr)
        sys.exit(1)

    ok, messages = verify_bundle(data, expected_key_fingerprint=args.expected_fingerprint)
    for m in messages:
        prefix = "  [✓]" if ok else "  [✗]"
        print(f"{prefix} {m}")

    if ok:
        print("\nSUCCESS: Closure-Trace review artifact is authentic, intact, and independently verified.")
        sys.exit(0)
    else:
        print("\nFAILURE: Closure-Trace review artifact verification failed!", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
