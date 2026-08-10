"""
Multi-criteria granularity evaluation tests for Intent Deviation (N) (v0.3).
Evaluates reliability alongside theoretical coherence, evidence requirements, and prevalence metrics.
"""

import pytest
from ec_framework import (
    evaluate_granularity,
    AnnotatorRating,
    AnnotationItemRecord,
    TrajectoryCategory,
)


def test_evaluate_granularity_multi_criteria():
    # Construct mock records for Event, Action, Episode
    granularity_data = {}

    for level in ["event", "action", "episode"]:
        records = []
        for i in range(10):
            cat1 = TrajectoryCategory.DIRECT_INTENT_PROGRESSION if i < 7 else TrajectoryCategory.INDIRECT_OR_DETOUR_BEHAVIOR
            cat2 = cat1
            r1 = AnnotatorRating("r1", f"{level}_{i}", cat1, "snippet", 1.0, "2026-08-10T12:00:00Z")
            r2 = AnnotatorRating("r2", f"{level}_{i}", cat2, "snippet", 1.0, "2026-08-10T12:00:00Z")
            records.append(AnnotationItemRecord(f"{level}_{i}", "Task I", (r1, r2)))
        granularity_data[level] = records

    results = evaluate_granularity(granularity_data)

    assert "event" in results
    assert "action" in results
    assert "episode" in results

    for level in ["event", "action", "episode"]:
        res = results[level]
        assert res["kappa_substantive"] == 1.0
        assert res["gwets_ac1_substantive"] == 1.0
        assert res["substantive_items_count"] == 10.0
        assert res["insufficient_evidence_prevalence"] == 0.0
