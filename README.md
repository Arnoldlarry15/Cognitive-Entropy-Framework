# Cognitive Entropy Framework (Ec)

A framework for measuring cognitive overload in digital environments,
built around a single scalar metric: **Ec (cognitive entropy cost)**.

Reference implementation of **MF-0.1** (Cognitive Entropy Measurement
Framework Version 0.1), dated 2026-07-12.

```
Ec = (Σ wi · xi) × (1 − Φ)
```

- `xi` — a candidate attention/workflow variable, normalized against a baseline
- `wi` — the weight assigned to that variable
- `Φ`  — a bounded [0, 1] dampening/correction term

## Status

Provisional (v0.1). Weight estimation, the empirical reference baseline
(Bref), and pilot/validation data are still open before this reaches v1.0.
See [`spec/MF-0.1.md`](spec/MF-0.1.md) for the full write-up and open items.

## Structure

```
cognitive-entropy-framework/
├── ec_framework/       # Python package: Variable, Baseline, EcModel
│   ├── core.py         # Ec functional implementation
│   └── baselines.py    # Theoretical / Reference (Bref) / Personal tiers
├── tests/              # pytest suite
├── spec/
│   └── MF-0.1.md        # the provisional spec
└── docs/                # supplementary notes, diagrams, pilot data writeups
```

## Install

```bash
pip install -e ".[dev]"
```

## Quickstart

```python
from ec_framework import Variable, EcModel, TheoreticalBaseline

variables = [
    Variable(name="tab_switches", weight=0.5),
    Variable(name="notification_count", weight=0.3),
]

baseline = TheoreticalBaseline({"tab_switches": 0, "notification_count": 0})
model = EcModel(variables, baseline=baseline)

readings = {"tab_switches": 10, "notification_count": 5}
ec_score = model.compute(readings, phi=0.0)

# Or get the per-variable breakdown:
breakdown = model.breakdown(readings, phi=0.0)
```

You define your own `Variable` set, weights, and `Φ` source — MF-0.1
leaves those as calibration work rather than fixing them, since the
reference baseline (Bref) hasn't been empirically established yet.

## Testing

```bash
pytest tests/ -v
```

## License

Code is licensed under [MIT](LICENSE). The spec document
(`spec/MF-0.1.md`) is licensed under [CC BY 4.0](LICENSE-SPEC.md) —
share and build on it freely, with attribution.

## Author

Larry Arnold ([@Arnoldlarry15](https://github.com/Arnoldlarry15))
