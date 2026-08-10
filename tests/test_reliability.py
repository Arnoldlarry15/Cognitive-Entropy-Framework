"""
Mathematical verification tests for inter-rater reliability suite (MF-0.1 v0.3).
Validates Cohen's Kappa, Fleiss' Kappa, Gwet's AC1, CIs, and dual reliability metrics
against independently established statistical literature benchmarks.
"""

import pytest
import math
from ec_framework import (
    cohens_kappa,
    fleiss_kappa,
    gwets_ac1,
    compute_confusion_matrix,
    compute_dual_reliability,
    AnnotatorRating,
    AnnotationItemRecord,
)


def test_cohens_kappa_literature_benchmark():
    """Validates Cohen's Kappa against standard textbook example matrix.
    
    Matrix: [[45, 5], [15, 35]] (Total N = 100)
    Po = 80 / 100 = 0.80
    Pe = (50/100)*(60/100) + (50/100)*(40/100) = 0.30 + 0.20 = 0.50
    Expected Kappa = (0.80 - 0.50) / (1 - 0.50) = 0.30 / 0.50 = 0.6000
    """
    r1 = ["A"] * 50 + ["B"] * 50
    r2 = ["A"] * 45 + ["B"] * 5 + ["A"] * 15 + ["B"] * 35

    res = cohens_kappa(r1, r2, categories=["A", "B"])

    assert math.isclose(res["po"], 0.80, abs_tol=1e-4)
    assert math.isclose(res["pe"], 0.50, abs_tol=1e-4)
    assert math.isclose(res["kappa"], 0.60, abs_tol=1e-4)
    assert res["ci_lower"] <= res["kappa"] <= res["ci_upper"]


def test_fleiss_kappa_textbook_benchmark():
    """Validates Fleiss' Kappa against Fleiss (1971) classic textbook benchmark.
    
    10 subjects, 4 raters, 3 categories.
    Matrix of counts:
    [0, 0, 4] -> P_1 = 1.0
    [0, 4, 0] -> P_2 = 1.0
    [2, 2, 0] -> P_3 = 0.3333
    [2, 2, 0] -> P_4 = 0.3333
    [0, 1, 3] -> P_5 = 0.5000
    [1, 1, 2] -> P_6 = 0.1667
    [3, 0, 1] -> P_7 = 0.5000
    [0, 0, 4] -> P_8 = 1.0
    [0, 0, 4] -> P_9 = 1.0
    [1, 3, 0] -> P_10 = 0.5000

    Calculated Po = 0.633333, Pe = 0.35875, Fleiss' Kappa = 0.4282 (approx 0.428)
    """
    matrix = [
        [0, 0, 4],
        [0, 4, 0],
        [2, 2, 0],
        [2, 2, 0],
        [0, 1, 3],
        [1, 1, 2],
        [3, 0, 1],
        [0, 0, 4],
        [0, 0, 4],
        [1, 3, 0],
    ]
    res = fleiss_kappa(matrix)

    assert math.isclose(res["po"], 0.633333, abs_tol=1e-4)
    assert math.isclose(res["pe"], 0.35875, abs_tol=1e-4)
    assert math.isclose(res["kappa"], 0.4282, abs_tol=1e-3)


def test_gwets_ac1_benchmark():
    """Validates Gwet's AC1 statistic against standard 2x2 matrix benchmark.
    
    Matrix: [[45, 5], [15, 35]]
    Po = 0.80
    pi_A = (0.50 + 0.60) / 2 = 0.55
    pi_B = (0.50 + 0.40) / 2 = 0.45
    e_gamma = 1/(2-1) * (0.55*0.45 + 0.45*0.55) = 0.495
    Expected AC1 = (0.80 - 0.495) / (1 - 0.495) = 0.305 / 0.505 = 0.603960...
    """
    r1 = ["A"] * 50 + ["B"] * 50
    r2 = ["A"] * 45 + ["B"] * 5 + ["A"] * 15 + ["B"] * 35

    res = gwets_ac1(r1, r2, categories=["A", "B"])

    assert math.isclose(res["po"], 0.80, abs_tol=1e-4)
    assert math.isclose(res["e_gamma"], 0.495, abs_tol=1e-4)
    assert math.isclose(res["ac1"], 0.60396, abs_tol=1e-4)


def test_perfect_and_chance_agreement():
    # 100% agreement
    r1 = ["A", "B", "C", "A"]
    r2 = ["A", "B", "C", "A"]
    assert cohens_kappa(r1, r2)["kappa"] == 1.0
    assert gwets_ac1(r1, r2)["ac1"] == 1.0

    # Opposite agreement
    r1 = ["A", "A", "B", "B"]
    r2 = ["B", "B", "A", "A"]
    assert cohens_kappa(r1, r2)["kappa"] < 0.0


def test_dual_reliability_breakdown():
    # Construct 10 items: 8 substantive, 2 INSUFFICIENT_EVIDENCE
    records = []
    for i in range(8):
        cat1 = "SYSTEM_PRESENTED" if i % 2 == 0 else "INTENT_INTRINSIC"
        cat2 = cat1  # perfect substantive agreement
        r1 = AnnotatorRating("r1", f"item_{i}", cat1, "snippet", 1.0, "2026-08-10T12:00:00Z")
        r2 = AnnotatorRating("r2", f"item_{i}", cat2, "snippet", 1.0, "2026-08-10T12:00:00Z")
        records.append(AnnotationItemRecord(f"item_{i}", "Task I", (r1, r2)))

    for i in range(8, 10):
        r1 = AnnotatorRating("r1", f"item_{i}", "INSUFFICIENT_EVIDENCE", "gaps", 1.0, "2026-08-10T12:00:00Z")
        r2 = AnnotatorRating("r2", f"item_{i}", "INSUFFICIENT_EVIDENCE", "gaps", 1.0, "2026-08-10T12:00:00Z")
        records.append(AnnotationItemRecord(f"item_{i}", "Task I", (r1, r2)))

    dual = compute_dual_reliability(records)

    assert dual["total_items"] == 10
    assert dual["substantive_items_count"] == 8
    assert dual["insufficient_evidence_count"] == 4  # 2 raters * 2 items = 4 ratings
    assert math.isclose(dual["kappa_substantive"], 1.0, abs_tol=1e-4)
    assert math.isclose(dual["gwets_ac1_substantive"], 1.0, abs_tol=1e-4)
    assert math.isclose(dual["kappa_evidence"], 1.0, abs_tol=1e-4)
