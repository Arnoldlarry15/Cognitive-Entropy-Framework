import pytest
from ec_framework import Variable, EcModel, TheoreticalBaseline


def test_basic_ec_computation():
    variables = [
        Variable(name="tab_switches", weight=0.5),
        Variable(name="notification_count", weight=0.3),
    ]
    model = EcModel(variables)
    readings = {"tab_switches": 10, "notification_count": 5}
    ec = model.compute(readings, phi=0.0)
    assert ec == pytest.approx(0.5 * 10 + 0.3 * 5)


def test_phi_dampens_score():
    variables = [Variable(name="x", weight=1.0)]
    model = EcModel(variables)
    ec_no_damp = model.compute({"x": 10}, phi=0.0)
    ec_damped = model.compute({"x": 10}, phi=0.5)
    assert ec_damped == pytest.approx(ec_no_damp * 0.5)


def test_phi_out_of_range_raises():
    variables = [Variable(name="x", weight=1.0)]
    model = EcModel(variables)
    with pytest.raises(ValueError):
        model.compute({"x": 10}, phi=1.5)


def test_missing_reading_raises():
    variables = [Variable(name="x", weight=1.0)]
    model = EcModel(variables)
    with pytest.raises(KeyError):
        model.compute({}, phi=0.0)


def test_baseline_adjustment_applied():
    variables = [Variable(name="x", weight=1.0)]
    baseline = TheoreticalBaseline({"x": 3})
    model = EcModel(variables, baseline=baseline)
    ec = model.compute({"x": 10}, phi=0.0)
    assert ec == pytest.approx(7.0)


def test_breakdown_returns_contributions():
    variables = [
        Variable(name="a", weight=0.5),
        Variable(name="b", weight=0.5),
    ]
    model = EcModel(variables)
    result = model.breakdown({"a": 4, "b": 6}, phi=0.0)
    assert result["contributions"]["a"] == pytest.approx(2.0)
    assert result["contributions"]["b"] == pytest.approx(3.0)
    assert result["ec"] == pytest.approx(5.0)
