# Cognitive Entropy Measurement Framework ($E_c$)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Specification](https://img.shields.io/badge/spec-MF--0.1-green.svg)](spec/MF-0.1.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Spec License: CC BY 4.0](https://img.shields.io/badge/Spec_License-CC_BY_4.0-lightgrey.svg)](LICENSE-SPEC.md)

> **"A rigorous, falsifiable engineering construct to quantify software coordination cost independently of task difficulty or user expertise."**

---

## 🌟 Overview & Motivation

Digital workflows increasingly demand that humans navigate complex mazes of application switching, authentication dialogs, notification interruptions, and arbitrary configuration decisions just to accomplish straightforward goals. Historically, software teams have discussed this burden using vague terms like "friction," "user fatigue," or "context switching"—concepts that lack standard, reproducible measurement.

The **Cognitive Entropy Framework ($E_c$)** bridges this gap. Version 0.1 (**MF-0.1**) introduces a baseline-independent measurement framework that quantifies **coordination cost** in digital workflows as an engineering construct: a normalized deviation between an observed workflow and an empirically established reference baseline.

### Key Contributions & Innovations
* **Isolates Overhead from Difficulty:** Through baseline normalization, $E_c$ measures system-imposed coordination overhead without conflating it with intrinsic task complexity or user skill (*Construct Validity*).
* **Baseline Independence:** Prevents circular evaluations by requiring reference baselines ($B_{ref}$) to be independently derived across expert populations—preventing tools from redefining "normal" to grade themselves favorably.
* **Multi-Layered Variable Taxonomy:** Defines candidate variables across structural, interaction, cognitive, and noise layers, alongside a bounded reduction factor ($\Phi$).
* **Falsifiable Science:** Formulated as a research specification designed to be tested, critiqued, and empirically calibrated rather than accepted as a closed standard.

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
| **Interaction** | $D$ | **Decision Overhead** | Ratio of system-imposed decisions (OAuth, scopes) vs. intent decisions. |
| **Interaction** | $I$ | **Interruption Frequency** | Rate of external interruptions (2FA, CAPTCHAs, forced popups). |
| **Cognitive** | $M$ | **Excess Working Memory** | Cognitive load held in memory solely due to software design (IDs, keys). |
| **Cognitive** | $R$ | **Excess Recovery Cost** | Time/effort required to resume productive work after an interruption. |
| **Noise** | $N$ | **Intent Deviation** | Proportion of non-intent-advancing actions caused by hidden UI/controls. |
| **Reduction** | $\Phi$ | **Coordination Efficiency** | Fraction of coordination overhead eliminated by integrated automation. |

---

## 🎯 Three-Tiered Baseline Structure

To answer the fundamental counterfactual question—*"Compared to what?"*—MF-0.1 specifies three distinct baseline tiers:

1. **Theoretical Baseline ($B_{theo}$):** The idealized, absolute minimum coordination theoretically required by the task class, independent of software implementation.
2. **Reference Baseline ($B_{ref}$):** The median empirical coordination cost measured from qualified expert participants under standard workflows. Used as the authoritative benchmark for evaluating tools.
3. **Personal Baseline ($B_u$):** An individual's historical coordination cost. Used strictly for personalized feedback and descriptive diagnostics—never for tool evaluation.

---

## 💻 Python Reference Implementation

This repository provides a clean, modular Python 3.10+ package (`ec_framework`) implementing the core functional and baseline mechanics.

### Installation

```bash
git clone https://github.com/Arnoldlarry15/cognitive-entropy-framework.git
cd cognitive-entropy-framework
pip install -e ".[dev]"
```

### Quickstart Example

```python
from ec_framework import (
    Variable, 
    EcModel, 
    TheoreticalBaseline, 
    ReferenceBaseline
)

# 1. Define candidate variables with weights and normalization rules
variables = [
    Variable(name="application_fragmentation", weight=0.35, description="Excess apps switched"),
    Variable(name="decision_overhead", weight=0.40, description="System-imposed decisions"),
    Variable(name="interruption_frequency", weight=0.25, description="External interruptions/min"),
]

# 2. Establish a baseline (e.g. Theoretical or Reference population baseline)
b_ref = ReferenceBaseline({
    "application_fragmentation": 1.0,
    "decision_overhead": 0.5,
    "interruption_frequency": 0.2,
})

# 3. Instantiate the Cognitive Entropy Model
model = EcModel(variables=variables, baseline=b_ref)

# 4. Input raw interaction traces / telemetry
raw_readings = {
    "application_fragmentation": 4.0,  # 3.0 excess over baseline
    "decision_overhead": 2.5,          # 2.0 excess over baseline
    "interruption_frequency": 1.2,     # 1.0 excess over baseline
}

# 5. Compute Ec score with Coordination Efficiency (Phi = 20% automation dampening)
ec_score = model.compute(raw_readings, phi=0.20)
print(f"Cognitive Entropy Score (Ec): {ec_score:.4f}")

# 6. Retrieve detailed per-variable breakdown
breakdown = model.breakdown(raw_readings, phi=0.20)
print("Contributions:", breakdown["contributions"])
```

---

## 🧪 Testing & Validation

The test suite validates score computation, baseline adjustments, edge case handling, and contribution breakdowns:

```bash
python -m pytest tests/ -v
```

---

## 📁 Repository Structure

```
cognitive-entropy-framework/
├── ec_framework/           # Python reference implementation
│   ├── core.py             # EcModel, Variable, and baseline math logic
│   └── baselines.py        # Theoretical, Reference (Bref), & Personal baselines
├── spec/
│   └── MF-0.1.md           # Authoritative specification document (v0.1)
├── tests/                  # Pytest validation suite
├── pyproject.toml          # Package metadata & build configuration
├── LICENSE                 # Software License (MIT)
├── LICENSE-SPEC.md         # Specification License (CC BY 4.0)
└── README.md               # Project documentation
```

---

## 📖 Full Specification & Open Work

The complete, unabridged specification is available in [`spec/MF-0.1.md`](spec/MF-0.1.md).

Current open research vectors prior to **v1.0**:
- [ ] Empirical estimation of variable weights ($w_i$) via pilot regression data.
- [ ] Large-sample data collection for establishing population Reference Baselines ($B_{ref}$).
- [ ] Validation of observational proxies for Cognitive Complexity variables ($M, R$).
- [ ] Cross-domain calibration studies (e.g. healthcare, education, finance).

---

## 📜 License & Citation

* **Source Code:** Released under the [MIT License](LICENSE).
* **Specification:** Released under [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE-SPEC.md).

### Citation
```bibtex
@techreport{arnold2026cognitive,
  author = {Larry Arnold},
  title = {Cognitive Entropy Measurement Framework Version 0.1 (MF-0.1): A Measurement Framework for Coordination Cost in Digital Workflows},
  year = {2026},
  month = {July},
  url = {https://github.com/Arnoldlarry15/cognitive-entropy-framework}
}
```

**Author:** Larry Arnold ([@Arnoldlarry15](https://github.com/Arnoldlarry15))
