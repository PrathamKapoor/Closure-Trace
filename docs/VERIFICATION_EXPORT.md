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
  "format_version": "closure_trace_bundle/1.0.0",
  "run_id": "run-0192348a-...",
  "organization_id": "org_...",
  "canonical_document": { ... },
  "canonical_digest": "3a8b...64 hex chars (SHA3-256)",
  "receipt": {
    "id": "rcpt_...",
    "algorithm_id": "ML-DSA-65",
    "public_key_b64": "4a7f...",
    "public_key_fingerprint": "1c3e...64 hex chars (SHA3-256)",
    "signature_b64": "b52a...",
    "created_at": 1791708600.0
  },
  "ledger": {
    "entry_hash": "e81d..."
  }
}
```

## Standalone Offline Verification CLI

The verification script `scripts/verify_review_artifact.py` performs independent cryptographic checks without requiring network access, server secrets, or database connectivity:

```bash
# Verify bundle document integrity and signature against the embedded key
python scripts/verify_review_artifact.py path/to/exported_bundle.json

# Authenticate signer identity against a trusted out-of-band key fingerprint
python scripts/verify_review_artifact.py path/to/exported_bundle.json --expected-fingerprint <TRUSTED_HEX_FINGERPRINT>
```

### Trust Boundary and Verification Semantics

Independent verification separates **document integrity** from **signer identity authentication**:

1. **Self-Contained Integrity Verification**: Verifies that the canonical document matches `canonical_digest`, the public key fingerprint is well-formed, and the digital signature is cryptographically valid under the embedded public key. This proves the document has not been altered since signature creation.
2. **Signer Identity Authentication**: Proves *who* authorized the review. Because an attacker could generate a new keypair and sign a forged document, verifying signer identity requires supplying `--expected-fingerprint <fingerprint>`. The trusted fingerprint must be obtained out-of-band from the authority (e.g. key management registry, supervisor directory, or deployment manifest).

### Verification Checks Performed

1. **Schema Integrity**: Validates all expected bundle fields and format version (`closure_trace_bundle/1.0.0`).
2. **Canonical Digest Recomputation**: Reconstructs the canonical JSON serialization according to RFC 8785 rules and calculates the SHA3-256 hash. Verifies an exact match against `canonical_digest`.
3. **Public Key Fingerprint Match**: Verifies the fingerprint matches `sha3_256(public_key)`. If `--expected-fingerprint` is provided, verifies that the public key matches the trusted fingerprint.
4. **Quantum-Safe Signature Verification**: Cryptographically verifies the digital signature (e.g., ML-DSA-65) over the document digest using the bundle's public key.
5. **Ledger Commitment Check**: Verifies presence of the audit ledger commitment hash.

Tampered documents or invalid signatures return exit code `1` with explicit diagnostic messages. Genuine bundles return exit code `0`.
