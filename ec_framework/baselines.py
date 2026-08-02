"""
Convenience subclasses for the three baseline tiers defined in MF-0.1:
theoretical, reference (Bref), and personal.

These are thin wrappers around Baseline so call sites are self-documenting.
Bref (the empirically established reference baseline) is still open
calibration work per the spec, so ReferenceBaseline ships empty by default.
"""

from .core import Baseline


class TheoreticalBaseline(Baseline):
    """An idealized, zero-overload reference point.

    Typically all-zero (or all-minimum) reference values, representing
    the theoretical floor against which observed entropy is measured.
    """
    def __init__(self, reference_values: dict | None = None):
        super().__init__(tier="theoretical", reference_values=reference_values or {})


class ReferenceBaseline(Baseline):
    """The empirical population reference baseline (Bref).

    Not yet established per MF-0.1 — populate reference_values once
    pilot/validation data across a representative population is available.
    """
    def __init__(self, reference_values: dict | None = None):
        super().__init__(tier="reference", reference_values=reference_values or {})


class PersonalBaseline(Baseline):
    """An individual's own historical baseline for self-relative tracking."""
    def __init__(self, reference_values: dict | None = None):
        super().__init__(tier="personal", reference_values=reference_values or {})
