"""
Cognitive Entropy Framework (Ec)

A framework for measuring cognitive overload in digital environments.
Reference implementation of MF-0.1 (Cognitive Entropy Measurement Framework
Version 0.1), updated with v0.2 telemetry protocols and v0.3 observational
annotation & reliability suites.
"""

from .core import Variable, Baseline, EcModel
from .baselines import TheoreticalBaseline, ReferenceBaseline, PersonalBaseline
from .telemetry import TelemetryEvent, InteractionSession, TelemetryParser
from .annotation import (
    DecisionCategory,
    TrajectoryCategory,
    DisagreementReason,
    AnnotatorRating,
    AnnotationItemRecord,
    AdjudicationRecord,
)
from .reliability import (
    cohens_kappa,
    fleiss_kappa,
    gwets_ac1,
    compute_confusion_matrix,
    compute_dual_reliability,
    evaluate_granularity,
)

__version__ = "0.3.0"

__all__ = [
    "Variable",
    "Baseline",
    "EcModel",
    "TheoreticalBaseline",
    "ReferenceBaseline",
    "PersonalBaseline",
    "TelemetryEvent",
    "InteractionSession",
    "TelemetryParser",
    "DecisionCategory",
    "TrajectoryCategory",
    "DisagreementReason",
    "AnnotatorRating",
    "AnnotationItemRecord",
    "AdjudicationRecord",
    "cohens_kappa",
    "fleiss_kappa",
    "gwets_ac1",
    "compute_confusion_matrix",
    "compute_dual_reliability",
    "evaluate_granularity",
]
