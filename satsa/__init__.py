"""Supervisory analytics and evidence verification for Closure-Trace.

The ``satsa`` package provides submission ingestion, canonical evidence
storage, analytical workers, risk assessment, human review, and TRUST-SAT
verification. It reuses the ``qsmlops`` platform's cryptography, identity,
database, and audit services.

See ``docs/SATSA_SYSTEM_ARCHITECTURE.md`` for component boundaries and
``docs/API_CONTRACT.md`` for the hosted API.
"""
from __future__ import annotations

__version__ = "0.16.0"
