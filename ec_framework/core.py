"""
Core implementation of the Ec (cognitive entropy cost) functional.

    Ec = (Σ wi * xi) * (1 - Φ)

where:
    xi = value of candidate variable i (normalized against a baseline)
    wi = weight assigned to variable i
    Φ  = a bounded [0, 1] correction/dampening term (e.g. adaptation,
         familiarity, or friction-offset factor)

This module is intentionally unopinionated about *which* eight variables
you use, or what Φ represents in your context, since MF-0.1 leaves weight
estimation and the reference baseline (Bref) as open calibration work.
Fill in your own Variable set and weights once you have pilot data.
"""

from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class Variable:
    """A single candidate variable (xi) in the Ec functional.

    name: short identifier, e.g. "tab_switch_rate"
    weight: wi, the linear weight applied to this variable
    normalize: optional function mapping a raw reading to a normalized
        value against the active baseline. Defaults to identity.
    description: human-readable note on what this variable captures.
    """
    name: str
    weight: float
    normalize: Callable[[float], float] = field(default=lambda x: x)
    description: str = ""

    def value(self, raw: float) -> float:
        return self.normalize(raw)


@dataclass
class Baseline:
    """A named reference point for normalizing raw variable readings.

    MF-0.1 defines a three-tiered baseline structure:
      - theoretical: an idealized, zero-overload reference
      - reference (Bref): an empirically established population baseline
      - personal: an individual's own historical baseline
    Each tier is represented as a Baseline instance holding per-variable
    reference values.
    """
    tier: str
    reference_values: dict = field(default_factory=dict)

    def get(self, variable_name: str, default: float = 0.0) -> float:
        return self.reference_values.get(variable_name, default)


class EcModel:
    """Computes Ec = (Σ wi * xi) * (1 - Φ) for a given set of variables."""

    def __init__(self, variables: list[Variable], baseline: Optional[Baseline] = None):
        self.variables = variables
        self.baseline = baseline

    def compute(self, raw_readings: dict, phi: float = 0.0) -> float:
        """
        raw_readings: dict mapping variable name -> raw measured value
        phi: the Φ dampening term, in [0, 1]
        """
        if not (0.0 <= phi <= 1.0):
            raise ValueError("phi must be in [0, 1]")

        weighted_sum = 0.0
        for var in self.variables:
            raw = raw_readings.get(var.name)
            if raw is None:
                raise KeyError(f"Missing reading for variable '{var.name}'")
            baseline_adjustment = self.baseline.get(var.name) if self.baseline else 0.0
            normalized = var.value(raw - baseline_adjustment)
            weighted_sum += var.weight * normalized

        return weighted_sum * (1.0 - phi)

    def breakdown(self, raw_readings: dict, phi: float = 0.0) -> dict:
        """Returns per-variable contributions alongside the final Ec score."""
        contributions = {}
        for var in self.variables:
            raw = raw_readings.get(var.name)
            if raw is None:
                raise KeyError(f"Missing reading for variable '{var.name}'")
            baseline_adjustment = self.baseline.get(var.name) if self.baseline else 0.0
            normalized = var.value(raw - baseline_adjustment)
            contributions[var.name] = var.weight * normalized

        ec = sum(contributions.values()) * (1.0 - phi)
        return {"contributions": contributions, "phi": phi, "ec": ec}
