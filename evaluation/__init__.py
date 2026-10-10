"""SAT-SA evaluation harness — separate from ``satsa/`` by design.

Holds evaluation code whose ground truth must stay independent of the
detectors being evaluated:

* ``evaluation.workload`` — the workload/prioritization-lift experiment.
* ``evaluation.baselines`` — literature-named statistical baselines
  (z-score, MAD, IQR, fixed-threshold, random, severity-only) plus a
  head-to-head comparison against a real SAT-SA worker's output on the
  same data (engineering notes to the implementation; import nothing from ``satsa.*`` so a
  baseline can never accidentally call the code it is compared
  against).
* ``evaluation.ablation`` — disables exactly one default worker at a
  time on an already-ingested scope and reports which finding
  families disappear, i.e. each worker's unique, non-overlapping
  contribution to detection coverage (engineering notes to the implementation).

Statistical significance/confidence-interval reporting across larger
synthetic cohorts remains not started (see docs/IMPLEMENTATION_NOTES.md).
Nothing in ``satsa/`` imports from here; this package imports *from*
``satsa`` to drive real runs, never the reverse.
"""
