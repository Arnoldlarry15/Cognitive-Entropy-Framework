"""
Unit tests for v0.3 annotation data models, technical immutability, and audit trails.
"""

import pytest
from dataclasses import FrozenInstanceError
from ec_framework import (
    AnnotatorRating,
    AnnotationItemRecord,
    AdjudicationRecord,
    DecisionCategory,
    TrajectoryCategory,
    DisagreementReason,
)


def test_annotator_rating_immutability():
    rating = AnnotatorRating(
        annotator_id="rater_1",
        item_id="item_100",
        category=DecisionCategory.SYSTEM_PRESENTED,
        evidence_snippet="OAuth provider modal presented on screen",
        confidence_score=0.9,
        timestamp="2026-08-10T12:00:00Z",
    )
    assert rating.annotator_id == "rater_1"
    assert rating.category == "SYSTEM_PRESENTED"

    # Attempt to mutate attribute MUST raise FrozenInstanceError
    with pytest.raises(FrozenInstanceError):
        rating.category = DecisionCategory.INTENT_INTRINSIC  # type: ignore

    with pytest.raises(FrozenInstanceError):
        rating.annotator_id = "rater_2"  # type: ignore


def test_annotation_item_record_immutability():
    r1 = AnnotatorRating(
        annotator_id="rater_1",
        item_id="item_101",
        category=DecisionCategory.SYSTEM_PRESENTED,
        evidence_snippet="Region dropdown select",
        timestamp="2026-08-10T12:00:00Z",
    )
    r2 = AnnotatorRating(
        annotator_id="rater_2",
        item_id="item_101",
        category=DecisionCategory.INTENT_INTRINSIC,
        evidence_snippet="Format choice",
        timestamp="2026-08-10T12:01:00Z",
    )

    record = AnnotationItemRecord(
        item_id="item_101",
        declared_task_intent="Export report as PDF",
        initial_ratings=(r1,),
    )

    # Initial ratings tuple MUST be immutable
    assert len(record.initial_ratings) == 1
    with pytest.raises(FrozenInstanceError):
        record.declared_task_intent = "New intent"  # type: ignore

    # Test adding a rating returns a NEW record instance
    record_v2 = record.with_added_rating(r2)
    assert len(record.initial_ratings) == 1  # Original record is UNCHANGED
    assert len(record_v2.initial_ratings) == 2  # New record contains both
    assert record_v2.initial_ratings[0] == r1
    assert record_v2.initial_ratings[1] == r2


def test_adjudication_audit_trail_preservation():
    r1 = AnnotatorRating(
        annotator_id="rater_1",
        item_id="item_102",
        category=TrajectoryCategory.DIRECT_INTENT_PROGRESSION,
        evidence_snippet="Code typed directly in target file",
        timestamp="2026-08-10T12:00:00Z",
    )
    r2 = AnnotatorRating(
        annotator_id="rater_2",
        item_id="item_102",
        category=TrajectoryCategory.INDIRECT_OR_DETOUR_BEHAVIOR,
        evidence_snippet="Opened docs tab for 15s",
        timestamp="2026-08-10T12:01:00Z",
    )

    item_record = AnnotationItemRecord(
        item_id="item_102",
        declared_task_intent="Build web component",
        initial_ratings=(r1, r2),
    )

    adj = AdjudicationRecord(item_id="item_102", initial_record=item_record)
    assert adj.adjudication_status == "UNADJUDICATED"

    # Perform adjudication
    adj.adjudicate(
        final_resolution=TrajectoryCategory.INDIRECT_OR_DETOUR_BEHAVIOR,
        reason=DisagreementReason.EVIDENCE_DEFICIT,
        notes="Annotator 1 missed the 15s docs tab focus in log trace",
    )

    assert adj.adjudication_status == "ADJUDICATED"
    assert adj.final_resolution == "INDIRECT_OR_DETOUR_BEHAVIOR"
    assert adj.adjudication_reason == DisagreementReason.EVIDENCE_DEFICIT

    # CRITICAL: Verify initial ratings were NOT mutated or overwritten during adjudication
    assert len(adj.initial_record.initial_ratings) == 2
    assert adj.initial_record.initial_ratings[0].category == TrajectoryCategory.DIRECT_INTENT_PROGRESSION
    assert adj.initial_record.initial_ratings[1].category == TrajectoryCategory.INDIRECT_OR_DETOUR_BEHAVIOR
