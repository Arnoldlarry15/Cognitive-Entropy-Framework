"""
Observational Annotation Data Models and Immutable Audit Trails for MF-0.1 (v0.3).

Epistemic & Technical Constraints:
1. Technical Immutability: AnnotatorRating and AnnotationItemRecord use frozen dataclasses.
   Initial ratings cannot be mutated after creation.
2. Observational (Non-Causal) Categories: Categories record observed system presentations
   (e.g., SYSTEM_PRESENTED) and behavioral trajectories (e.g., INDIRECT_OR_DETOUR_BEHAVIOR),
   NOT inferred internal causes.
3. Adjudication vs. Ground Truth: Adjudication produces an adjudicated dataset resolution
   (final_resolution) for benchmark comparison, NOT scientifically validated ground truth.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple, List, Optional, Dict, Any


class DecisionCategory(str, Enum):
    """Observational categories for Decision Overhead (D)."""
    INTENT_INTRINSIC = "INTENT_INTRINSIC"
    SYSTEM_PRESENTED = "SYSTEM_PRESENTED"
    DUAL_OR_CONTEXT_DEPENDENT = "DUAL_OR_CONTEXT_DEPENDENT"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class TrajectoryCategory(str, Enum):
    """Observational categories for Intent Deviation (N)."""
    DIRECT_INTENT_PROGRESSION = "DIRECT_INTENT_PROGRESSION"
    INDIRECT_OR_DETOUR_BEHAVIOR = "INDIRECT_OR_DETOUR_BEHAVIOR"
    TASK_DISCONNECTED_BEHAVIOR = "TASK_DISCONNECTED_BEHAVIOR"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class DisagreementReason(str, Enum):
    """Taxonomy of root causes for rating disagreement assigned during adjudication."""
    DEFINITION_AMBIGUITY = "DEFINITION_AMBIGUITY"
    EVIDENCE_DEFICIT = "EVIDENCE_DEFICIT"
    ANNOTATOR_DISAGREEMENT = "ANNOTATOR_DISAGREEMENT"
    BEHAVIORAL_AMBIGUITY = "BEHAVIORAL_AMBIGUITY"
    ANNOTATOR_ERROR = "ANNOTATOR_ERROR"
    TASK_CONTEXT_EFFECT = "TASK_CONTEXT_EFFECT"


@dataclass(frozen=True)
class AnnotatorRating:
    """An immutable single annotator rating for a given task item.
    
    Attributes:
        annotator_id: Unique string identifier for the annotator.
        item_id: Unique string identifier for the target item (event, action, or episode).
        category: Rating category string (e.g. 'SYSTEM_PRESENTED').
        evidence_snippet: Required visual/text snippet or timestamp range supporting rating.
        confidence_score: Metadata score [0.0, 1.0] representing annotator self-reported certainty.
                          NOTE: Confidence is metadata ONLY and does NOT weight reliability calculations.
        timestamp: ISO timestamp string of when the rating was recorded.
    """
    annotator_id: str
    item_id: str
    category: str
    evidence_snippet: str
    confidence_score: float = 1.0
    timestamp: str = ""

    def __post_init__(self):
        if not (0.0 <= self.confidence_score <= 1.0):
            raise ValueError("confidence_score must be in range [0.0, 1.0]")


@dataclass(frozen=True)
class AnnotationItemRecord:
    """An immutable collection of independent annotator ratings for a single item.
    
    Attributes:
        item_id: Unique item identifier.
        declared_task_intent: Pre-declared task goal (I_task) established BEFORE the session.
        initial_ratings: Immutable tuple of initial independent ratings.
    """
    item_id: str
    declared_task_intent: str
    initial_ratings: Tuple[AnnotatorRating, ...] = field(default_factory=tuple)

    def with_added_rating(self, rating: AnnotatorRating) -> "AnnotationItemRecord":
        """Returns a NEW instance of AnnotationItemRecord with the added rating.
        Does NOT mutate existing instance (enforcing technical immutability).
        """
        if rating.item_id != self.item_id:
            raise ValueError(f"Rating item_id '{rating.item_id}' does not match record item_id '{self.item_id}'")
        new_ratings = self.initial_ratings + (rating,)
        return AnnotationItemRecord(
            item_id=self.item_id,
            declared_task_intent=self.declared_task_intent,
            initial_ratings=new_ratings,
        )


@dataclass
class AdjudicationRecord:
    """Post-rating adjudication record preserving initial ratings and audit metadata.
    
    NOTE: Adjudication produces an adjudicated dataset resolution for benchmark comparison,
    NOT an objectively correct or validated scientific ground truth.
    """
    item_id: str
    initial_record: AnnotationItemRecord
    adjudication_status: str = "UNADJUDICATED"  # 'UNADJUDICATED', 'AGREED', 'ADJUDICATED'
    adjudication_reason: Optional[DisagreementReason] = None
    final_resolution: Optional[str] = None  # Adjudicated dataset resolution label
    adjudication_notes: str = ""

    def adjudicate(self, final_resolution: str, reason: Optional[DisagreementReason] = None, notes: str = "") -> None:
        """Sets adjudication metadata without altering initial_record.initial_ratings."""
        self.final_resolution = final_resolution
        self.adjudication_reason = reason
        self.adjudication_notes = notes
        
        # Check if initial ratings agreed
        categories = {r.category for r in self.initial_record.initial_ratings}
        if len(categories) <= 1:
            self.adjudication_status = "AGREED"
        else:
            self.adjudication_status = "ADJUDICATED"
