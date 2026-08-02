"""
Cognitive Entropy Framework (Ec)

A framework for measuring cognitive overload in digital environments.
Reference implementation of MF-0.1 (Cognitive Entropy Measurement Framework
Version 0.1), dated 2026-07-12.
"""

from .core import Variable, Baseline, EcModel
from .baselines import TheoreticalBaseline, ReferenceBaseline, PersonalBaseline

__version__ = "0.1.0"

__all__ = [
    "Variable",
    "Baseline",
    "EcModel",
    "TheoreticalBaseline",
    "ReferenceBaseline",
    "PersonalBaseline",
]
