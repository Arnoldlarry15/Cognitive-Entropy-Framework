# Cognitive Entropy Measurement Framework ($E_c$)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Specification](https://img.shields.io/badge/spec-MF--0.1-green.svg)](spec/MF-0.1.md)
[![v0.2 Telemetry Spec](https://img.shields.io/badge/spec-v0.2--telemetry-blue.svg)](spec/v0.2-spec-notes.md)
[![v0.3 Observational Annotation Spec](https://img.shields.io/badge/spec-v0.3--annotation-purple.svg)](spec/v0.3-spec-notes.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Spec License: CC BY 4.0](https://img.shields.io/badge/Spec_License-CC_BY_4.0-lightgrey.svg)](LICENSE-SPEC.md)

> **"A rigorous, falsifiable engineering construct to quantify software coordination cost independently of task difficulty or user expertise."**

---

## 🌟 Overview & Motivation

Digital workflows increasingly demand that humans navigate complex mazes of application switching, authentication dialogs, notification interruptions, and arbitrary configuration decisions just to accomplish straightforward goals. Historically, software teams have discussed this burden using vague terms like "friction," "user fatigue," or "context switching"—concepts that lack standard, reproducible measurement.

The **Cognitive Entropy Framework ($E_c$)** bridges this gap. Version 0.1 (**MF-0.1**) introduces a baseline-independent measurement framework that quantifies **coordination cost** in digital workflows as an engineering construct: a normalized deviation between an observed workflow and an empirically established reference baseline.

### Core Epistemic Governance Rules (v0.3)
* **Epistemic Hierarchy:**  
  $$\text{Instrumentation} \neq \text{Measurement} \neq \text{Validation} \neq \text{Theory}$$
* **Raw Signals Are Candidate Inputs:** Logging telemetry events ($A_{raw}, S_{raw}, I_{raw}$) does not make them validated measurements.
* **Observational (Non-Causal) Rubrics:** Rubrics label observed system presentations (`SYSTEM_PRESENTED`) and behavioral trajectories (`INDIRECT_OR_DETOUR_BEHAVIOR`), NOT inferred internal causes.
* **Technical Immutability:** Initial independent ratings (`initial_ratings`) are stored as frozen, immutable records. Adjudication creates an audit trail (`final_resolution`), NOT scientifically validated ground truth.
* **Dual Reliability Mathematics:** Computes $\kappa_{\text{substantive}}$ (excluding `INSUFFICIENT_EVIDENCE`), $\kappa_{\text{evidence}}$, and **Gwet's AC1** to diagnose prevalence paradoxes.
* **Strict Construct Scope:** $E_c$ measures digital system coordination overhead. It does not attempt to be a general theory of human cognition.

---

## 📐 The Mathematical Functional

In MF-0.1, Cognitive Entropy ($E_c$) is computed via a provisional linear-dampened functional:

$$E_c = \left( \sum_{i} w_i \cdot x_i \right) \times (1 - \Phi)$$

Where:
* $x_i \in [0, 1]$ — The normalized, baseline-adjusted excess value of candidate variable $i$.
* $w_i$ — The importance weight for variable $i$ (reserved for empirical regression against completion times, error rates, and workload metrics).
* $\Phi \in [0, 1]$ — **Coordination Efficiency**, representing the fraction of coordination burden eliminated by automation or integrated tooling.

---

## 🧬 Variable Taxonomy (MF-0.1)

MF-0.1 defines eight candidate variables grouped across four physical and psychological complexity layers, plus a reduction term:

| Layer | Symbol | Variable Name | Description |
| :--- | :--- | :--- | :--- |
| **Structural** | $A$ | **Application Fragmentation** | Excess distinct digital environments traversed beyond $B_{theo}$. |
| **Structural** | $S$ | **Context Transition Frequency** | Rate of required shifts between independent cognitive environments. |
| **Interaction** | $D$ | **Decision Overhead** | Ratio of system-presented decisions vs. intent decisions. |
| **Interaction** | $I$ | **Interruption Frequency** | Rate of external interruptions (2FA, CAPTCHAs, forced popups). |
| **Cognitive** | $M$ | **Excess Working Memory** | Cognitive load held in memory solely due to software design ($M_{\text{proxy}}$). |
| **Cognitive** | $R$ | **Excess Recovery Cost** | Time/effort required to resume productive work after an interruption. |
| **Noise** | $N$ | **Intent Deviation** | Proportion of non-intent-advancing actions caused by hidden UI/controls. |
| **Reduction** | $\Phi$ | **Coordination Efficiency** | Fraction of coordination overhead eliminated by integrated automation. |

---

## 💻 Python Reference Implementation

The `ec_framework` Python 3.10+ package provides:
- Core model & baseline calculations (`core.py`, `baselines.py`).
- Telemetry log parser for raw candidate signal extraction (`telemetry.py`).
- Immutable observational annotation data models & audit trails (`annotation.py`).
- Inter-rater reliability calculation suite ($\kappa_{\text{substantive}}$, $\kappa_{\text{evidence}}$, Gwet's AC1, Fleiss' $\kappa$, 95% CIs) (`reliability.py`).

### Quickstart: Observational Annotation & Reliability Suite (v0.3)

```python
from ec_framework import (
    AnnotatorRating,
    AnnotationItemRecord,
    DecisionCategory,
    compute_dual_reliability,
    cohens_kappa,
    gwets_ac1
)

# 1. Create immutable independent ratings for a Decision point (D)
r1 = AnnotatorRating(
    annotator_id="rater_1",
    item_id="dec_001",
    category=DecisionCategory.SYSTEM_PRESENTED,
    evidence_snippet="OAuth provider modal presented",
    confidence_score=0.95,
    timestamp="2026-08-10T12:00:00Z"
)

r2 = AnnotatorRating(
    annotator_id="rater_2",
    item_id="dec_001",
    category=DecisionCategory.SYSTEM_PRESENTED,
    evidence_snippet="Interface required login choice",
    confidence_score=0.80,
    timestamp="2026-08-10T12:01:00Z"
)

# 2. Store in an immutable AnnotationItemRecord with pre-declared task intent (I_task)
record = AnnotationItemRecord(
    item_id="dec_001",
    declared_task_intent="Export report as PDF",
    initial_ratings=(r1, r2)
)

# 3. Compute Dual Reliability (Substantive vs Evidence) & Gwet's AC1
dual_res = compute_dual_reliability([record])
print(f"Substantive Cohen's Kappa: {dual_res['kappa_substantive']:.4f}")
print(f"Substantive Gwet's AC1:    {dual_res['gwets_ac1_substantive']:.4f}")
```

---

## 🧪 Testing & Validation

Run the complete 18-test suite:

```bash
python -m pytest tests/ -v
```

---

## 📁 Repository Structure

```
cognitive-entropy-framework/
├── ec_framework/           # Python reference implementation
│   ├── core.py             # EcModel, Variable, & baseline math logic
│   ├── baselines.py        # Theoretical, Reference (Bref), & Personal baselines
│   ├── telemetry.py        # v0.2 Telemetry parser & raw signal extraction
│   ├── annotation.py       # v0.3 Immutable annotation records & rubrics
│   └── reliability.py      # v0.3 Cohen's κ, Fleiss' κ, Gwet's AC1, & CIs
├── spec/
│   ├── MF-0.1.md           # Authoritative specification document (v0.1)
│   ├── v0.2-spec-notes.md   # v0.2 Telemetry protocol addendum
│   └── v0.3-spec-notes.md   # v0.3 Observational Annotation & Reliability spec
├── tests/
│   ├── test_core.py        # Model math tests
│   ├── test_telemetry.py   # v0.2 Telemetry parser tests (3 tests)
│   ├── test_annotation.py  # v0.3 Immutability & audit trail tests (3 tests)
│   ├── test_reliability.py # v0.3 Mathematical verification tests (5 tests)
│   └── test_granularity.py # v0.3 Multi-criteria granularity tests (1 test)
├── pyproject.toml          # Package metadata & dependencies
├── LICENSE                 # Software License (MIT)
├── LICENSE-SPEC.md         # Specification License (CC BY 4.0)
└── README.md               # Project documentation
```

---

## 📖 Roadmap to v1.0

- [x] **v0.1:** Provisional Specification & Mathematical Functional
- [x] **v0.2:** Telemetry Protocol & Raw Candidate Signal Parser
- [x] **v0.3:** Observational Annotation Rubrics, Immutability, & Dual Reliability Suite
- [ ] **v0.4:** Passive Proxy Empirical Validation Protocols & $B_{ref}$ Distribution Schema
- [ ] **v0.5:** Weight Regression Calibration & Construct Validity Test Suite
- [ ] **v0.6:** Task Ontology Formalization & Multi-Domain Benchmarks
- [ ] **v1.0:** Validated Specification Release & Published Population $B_{ref}$ Registry

---

## 📜 License & Citation

* **Source Code:** Released under the [MIT License](LICENSE).
* **Specification:** Released under [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE-SPEC.md).

### Citation
```bibtex
@techreport{arnold2026cognitive,
  author = {Larry Arnold},
  title = {Cognitive Entropy Measurement Framework (MF-0.1): A Measurement Framework for Coordination Cost in Digital Workflows},
  year = {2026},
  url = {https://github.com/Arnoldlarry15/cognitive-entropy-framework}
}
```

**Author:** Larry Arnold ([@Arnoldlarry15](https://github.com/Arnoldlarry15))
