# Portable Review Artifact Verification

## Overview

Closure-Trace provides cryptographic, verifiable review decisions backed by ML-DSA-65 post-quantum signatures and SHA3-256 digest trees.

To ensure non-repudiation and external auditability, review artifacts can be verified independently without requiring access to the server, its databases, or any signing keys.

## Export API Endpoint

```http
GET /api/v1/runs/{run_id}/export
```

**Access Control**: Requires supervisory permission (`satsa:read`).

### Export Bundle Schema

```json
{
  "run_id": "run-0192348a-...",
  "canonical_document": { ... },
  "digest_sha3_256": "3a8b...64 hex chars",
  "public_key_ml_dsa_65_hex": "4a7f...",
  "public_key_fingerprint": "1c3e...",
  "signature_ml_dsa_65_hex": "b52a...",
  "ledger_hash": "e81d...",
  "exported_at": 1791708600.0,
  "service": "Closure-Trace",
  "verification_instructions": "Verify using scripts/verify_review_artifact.py"
}
```

## Standalone Offline Verification CLI

The verification script `scripts/verify_review_artifact.py` relies exclusively on the public key and canonical document contained within the bundle:

```bash
# Verify a review bundle JSON file
python scripts/verify_review_artifact.py path/to/exported_bundle.json
```

### Verification Checks Performed

1. **Schema Integrity**: Validates all expected bundle fields are present.
2. **Canonical Digest Recomputation**: Reconstructs the canonical JSON serialization according to RFC 8785 rules and calculates the SHA3-256 hash. Verifies match against `digest_sha3_256`.
3. **Public Key Fingerprint Match**: Verifies the fingerprint matches `sha3_256(public_key)[:16]`.
4. **ML-DSA-65 Signature Verification**: Cryptographically verifies the digital signature against the recomputed document digest using the bundle's public key.

Tampered documents or invalid signatures return exit code `1` with explicit diagnostic messages. Genuine bundles return exit code `0`.
