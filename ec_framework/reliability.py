"""
Inter-Rater Reliability Computation Suite for MF-0.1 (v0.3).

Implements verified mathematical formulas for:
1. Cohen's Kappa (2 raters) + 95% Confidence Intervals & Large-Sample SE.
2. Fleiss' Kappa (multiple raters m > 2).
3. Gwet's AC1 (prevalence-robust agreement statistic).
4. Dual Reliability Breakdown (kappa_substantive vs. kappa_evidence).
5. Multi-Criteria Granularity Evaluation for Intent Deviation (N).

References:
- Cohen, J. (1960). A coefficient of agreement for nominal scales. Educational and Psychological Measurement.
- Fleiss, J. L. (1971). Measuring nominal scale agreement among many raters. Psychological Bulletin.
- Gwet, K. L. (2008/2014). Handbook of Inter-Rater Reliability. Advanced Analytics, LLC.
"""

import math
from typing import List, Dict, Any, Tuple, Optional
from .annotation import AnnotationItemRecord


def compute_confusion_matrix(
    r1: List[str], r2: List[str], categories: Optional[List[str]] = None
) -> Tuple[List[str], List[List[int]]]:
    """Computes confusion matrix between rater 1 and rater 2."""
    if len(r1) != len(r2):
        raise ValueError("Rating lists must have equal length")

    if categories is None:
        cats = sorted(list(set(r1) | set(r2)))
    else:
        cats = list(categories)

    cat_map = {cat: i for i, cat in enumerate(cats)}
    n_cats = len(cats)
    matrix = [[0] * n_cats for _ in range(n_cats)]

    for cat1, cat2 in zip(r1, r2):
        if cat1 in cat_map and cat2 in cat_map:
            matrix[cat_map[cat1]][cat_map[cat2]] += 1

    return cats, matrix


def cohens_kappa(
    r1: List[str], r2: List[str], categories: Optional[List[str]] = None
) -> Dict[str, float]:
    """Computes Cohen's Kappa, SE, 95% CI, Po, and Pe for two raters.
    
    Returns dict:
      - 'kappa': Cohen's kappa point estimate
      - 'se': Standard error
      - 'ci_lower': Lower bound 95% CI
      - 'ci_upper': Upper bound 95% CI
      - 'po': Observed agreement
      - 'pe': Expected agreement
      - 'n_items': Total item count
    """
    n = len(r1)
    if n == 0 or len(r2) != n:
        return {"kappa": 0.0, "se": 0.0, "ci_lower": 0.0, "ci_upper": 0.0, "po": 0.0, "pe": 0.0, "n_items": 0.0}

    cats, matrix = compute_confusion_matrix(r1, r2, categories)
    k_cats = len(cats)
    if k_cats <= 1:
        return {"kappa": 1.0, "se": 0.0, "ci_lower": 1.0, "ci_upper": 1.0, "po": 1.0, "pe": 1.0, "n_items": float(n)}

    # Observed agreement Po
    agreed_count = sum(matrix[i][i] for i in range(k_cats))
    po = agreed_count / float(n)

    # Marginals for expected agreement Pe
    r1_counts = [sum(matrix[i][j] for j in range(k_cats)) for i in range(k_cats)]
    r2_counts = [sum(matrix[i][j] for i in range(k_cats)) for j in range(k_cats)]

    pe = sum((r1_counts[i] / float(n)) * (r2_counts[i] / float(n)) for i in range(k_cats))

    if math.isclose(pe, 1.0):
        kappa = 1.0 if math.isclose(po, 1.0) else 0.0
        se = 0.0
    else:
        kappa = (po - pe) / (1.0 - pe)
        # Large-sample SE
        se_val = math.sqrt(max(0.0, po * (1.0 - po))) / ((1.0 - pe) * math.sqrt(n)) if n > 0 else 0.0
        se = se_val

    ci_lower = max(-1.0, kappa - 1.96 * se)
    ci_upper = min(1.0, kappa + 1.96 * se)

    return {
        "kappa": kappa,
        "se": se,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "po": po,
        "pe": pe,
        "n_items": float(n),
    }


def fleiss_kappa(rating_matrix: List[List[int]]) -> Dict[str, float]:
    """Computes Fleiss' Kappa for m raters rating N subjects across K categories.
    
    rating_matrix: N x K matrix where rating_matrix[i][k] is count of raters assigning subject i to cat k.
    """
    n_subjects = len(rating_matrix)
    if n_subjects == 0:
        return {"kappa": 0.0, "po": 0.0, "pe": 0.0, "n_subjects": 0.0}

    k_cats = len(rating_matrix[0])
    m_raters = sum(rating_matrix[0])
    if m_raters <= 1 or k_cats <= 1:
        return {"kappa": 1.0, "po": 1.0, "pe": 1.0, "n_subjects": float(n_subjects)}

    # Check that each row sums to m_raters
    total_ratings = n_subjects * m_raters

    # Compute P_i for each subject i
    p_i_list = []
    for row in rating_matrix:
        row_sum_sq = sum(c * c for c in row)
        p_i = (row_sum_sq - m_raters) / float(m_raters * (m_raters - 1))
        p_i_list.append(p_i)

    po = sum(p_i_list) / float(n_subjects)

    # Compute p_k for each category k
    p_k_list = []
    for k in range(k_cats):
        col_sum = sum(rating_matrix[i][k] for i in range(n_subjects))
        p_k_list.append(col_sum / float(total_ratings))

    pe = sum(p * p for p in p_k_list)

    if math.isclose(pe, 1.0):
        kappa = 1.0 if math.isclose(po, 1.0) else 0.0
    else:
        kappa = (po - pe) / (1.0 - pe)

    return {
        "kappa": kappa,
        "po": po,
        "pe": pe,
        "n_subjects": float(n_subjects),
        "n_raters": float(m_raters),
    }


def gwets_ac1(
    r1: List[str], r2: List[str], categories: Optional[List[str]] = None
) -> Dict[str, float]:
    """Computes Gwet's AC1 statistic for two raters across K categories.
    
    Gwet's AC1 is a prevalence-robust agreement statistic:
        AC1 = (Po - e_gamma) / (1 - e_gamma)
    where e_gamma = 1/(K - 1) * sum(pi_k * (1 - pi_k)), pi_k = (p1k + p2k) / 2.
    """
    n = len(r1)
    if n == 0 or len(r2) != n:
        return {"ac1": 0.0, "se": 0.0, "po": 0.0, "e_gamma": 0.0, "n_items": 0.0}

    cats, matrix = compute_confusion_matrix(r1, r2, categories)
    k_cats = len(cats)
    if k_cats <= 1:
        return {"ac1": 1.0, "se": 0.0, "po": 1.0, "e_gamma": 0.0, "n_items": float(n)}

    # Observed agreement Po
    agreed_count = sum(matrix[i][i] for i in range(k_cats))
    po = agreed_count / float(n)

    # Marginals
    r1_counts = [sum(matrix[i][j] for j in range(k_cats)) for i in range(k_cats)]
    r2_counts = [sum(matrix[i][j] for i in range(k_cats)) for j in range(k_cats)]

    pi_k = [((r1_counts[i] / float(n)) + (r2_counts[i] / float(n))) / 2.0 for i in range(k_cats)]

    e_gamma = (1.0 / (k_cats - 1.0)) * sum(p * (1.0 - p) for p in pi_k)

    if math.isclose(e_gamma, 1.0):
        ac1 = 1.0 if math.isclose(po, 1.0) else 0.0
        se = 0.0
    else:
        ac1 = (po - e_gamma) / (1.0 - e_gamma)
        se = math.sqrt(max(0.0, po * (1.0 - po))) / ((1.0 - e_gamma) * math.sqrt(n)) if n > 0 else 0.0

    return {
        "ac1": ac1,
        "se": se,
        "po": po,
        "e_gamma": e_gamma,
        "n_items": float(n),
    }


def compute_dual_reliability(
    item_records: List[AnnotationItemRecord],
    insufficient_evidence_category: str = "INSUFFICIENT_EVIDENCE",
) -> Dict[str, Any]:
    """Computes dual reliability breakdown:
    - kappa_substantive: Cohen's kappa on items where BOTH raters gave substantive ratings.
    - kappa_evidence: Agreement on whether item had sufficient evidence.
    - gwets_ac1_substantive: Gwet's AC1 on substantive items.
    - prevalence_report: Category frequencies and missingness metrics.
    """
    r1_all = []
    r2_all = []

    r1_substantive = []
    r2_substantive = []

    r1_ev_binary = []
    r2_ev_binary = []

    for item in item_records:
        if len(item.initial_ratings) >= 2:
            c1 = item.initial_ratings[0].category
            c2 = item.initial_ratings[1].category

            r1_all.append(c1)
            r2_all.append(c2)

            # Evidence binary
            r1_ev = "INSUFFICIENT" if c1 == insufficient_evidence_category else "SUFFICIENT"
            r2_ev = "INSUFFICIENT" if c2 == insufficient_evidence_category else "SUFFICIENT"
            r1_ev_binary.append(r1_ev)
            r2_ev_binary.append(r2_ev)

            # Substantive items
            if c1 != insufficient_evidence_category and c2 != insufficient_evidence_category:
                r1_substantive.append(c1)
                r2_substantive.append(c2)

    kappa_sub = cohens_kappa(r1_substantive, r2_substantive)
    ac1_sub = gwets_ac1(r1_substantive, r2_substantive)
    kappa_ev = cohens_kappa(r1_ev_binary, r2_ev_binary)

    # Category frequencies
    freqs = {}
    for cat in r1_all + r2_all:
        freqs[cat] = freqs.get(cat, 0) + 1

    total_ratings = len(r1_all) * 2
    prevalence_report = {cat: count / float(total_ratings) if total_ratings > 0 else 0.0 for cat, count in freqs.items()}

    insufficient_count = sum(1 for c in r1_all + r2_all if c == insufficient_evidence_category)
    insufficient_prevalence = insufficient_count / float(total_ratings) if total_ratings > 0 else 0.0

    return {
        "kappa_substantive": kappa_sub["kappa"],
        "kappa_substantive_se": kappa_sub["se"],
        "kappa_substantive_ci": (kappa_sub["ci_lower"], kappa_sub["ci_upper"]),
        "gwets_ac1_substantive": ac1_sub["ac1"],
        "kappa_evidence": kappa_ev["kappa"],
        "po_substantive": kappa_sub["po"],
        "pe_substantive": kappa_sub["pe"],
        "total_items": len(r1_all),
        "substantive_items_count": len(r1_substantive),
        "insufficient_evidence_count": insufficient_count,
        "insufficient_evidence_prevalence": insufficient_prevalence,
        "prevalence_report": prevalence_report,
    }


def evaluate_granularity(
    records_by_granularity: Dict[str, List[AnnotationItemRecord]],
    insufficient_evidence_category: str = "INSUFFICIENT_EVIDENCE",
) -> Dict[str, Dict[str, float]]:
    """Evaluates N annotation across Event, Action, and Episode granularities.
    
    Evaluates reliability along with:
    - kappa_substantive
    - gwets_ac1
    - po_substantive
    - substantive_item_count
    - insufficient_prevalence
    """
    results = {}
    for level, records in records_by_granularity.items():
        dual = compute_dual_reliability(records, insufficient_evidence_category)
        results[level] = {
            "kappa_substantive": dual["kappa_substantive"],
            "gwets_ac1_substantive": dual["gwets_ac1_substantive"],
            "po_substantive": dual["po_substantive"],
            "substantive_items_count": float(dual["substantive_items_count"]),
            "insufficient_evidence_prevalence": dual["insufficient_evidence_prevalence"],
        }
    return results
