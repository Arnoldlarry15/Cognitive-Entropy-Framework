# Cognitive Entropy Measurement Framework — Version 0.1 (MF-0.1)

**Date:** 2026-07-12
**Status:** Provisional. Weight estimation, the empirical reference baseline
(Bref), and pilot/validation data are still open work before this becomes v1.0.

---

## 1. Purpose

MF-0.1 is a conceptual framework for measuring cognitive overload in digital
environments. It introduces a single scalar metric, **Ec (cognitive entropy
cost)**, computed as a weighted linear combination of attention and workflow
variables, dampened by a correction term.

## 2. Ontology

*(Paste in your ontology section from the working spec — the categories and
definitions for what counts as an "attention variable" vs a "workflow
variable," and how they relate to the Ec construct.)*

## 3. Design Principles

*(Paste in your design principles section here.)*

## 4. Baseline Structure

Three tiers, per MF-0.1:

- **Theoretical** — an idealized, zero-overload reference point.
- **Reference (Bref)** — an empirically established population baseline.
  Not yet established; requires pilot/validation data across a
  representative population.
- **Personal** — an individual's own historical baseline, for
  self-relative tracking over time.

## 5. Candidate Variables

MF-0.1 defines eight candidate variables (xi). List them here with their
definitions and measurement source:

1.
2.
3.
4.
5.
6.
7.
8.

## 6. The Ec Functional

```
Ec = (Σ wi · xi) × (1 − Φ)
```

- `xi` — value of candidate variable i, normalized against the active baseline
- `wi` — weight assigned to variable i (open calibration work)
- `Φ`  — a bounded [0, 1] correction/dampening term

## 7. Open Work Toward v1.0

- [ ] Estimate weights (wi) for each candidate variable
- [ ] Establish the reference baseline (Bref) from pilot data
- [ ] Run pilot/validation study
- [ ] Define Φ precisely and how it's measured/estimated
- [ ] Peer review / external validation of the ontology

---

*This file is a structural placeholder mirroring the sections of the
working MF-0.1 draft. Drop in the full text of your provisional spec to
replace the placeholder notes above.*
