"""
Unit tests for v0.2 telemetry protocol and candidate raw signal extraction.
"""

import pytest
from ec_framework import TelemetryEvent, InteractionSession, TelemetryParser


def test_telemetry_event_from_dict():
    data = {
        "timestamp": "2026-08-10T12:00:00.000Z",
        "session_id": "sess_001",
        "event_type": "environment_switch",
        "source_app": "VSCode",
        "target_app": "Chrome",
        "environment_id": "env_docs",
        "metadata": {"dwell_time_ms": 3500},
    }
    evt = TelemetryEvent.from_dict(data)
    assert evt.session_id == "sess_001"
    assert evt.source_app == "VSCode"
    assert evt.target_app == "Chrome"
    assert evt.metadata["dwell_time_ms"] == 3500


def test_telemetry_parser_jsonl():
    jsonl_data = """
    {"timestamp": "2026-08-10T12:00:00.000Z", "session_id": "sess_001", "event_type": "interaction", "source_app": "VSCode", "environment_id": "env_ide", "metadata": {"dwell_time_ms": 5000}}
    {"timestamp": "2026-08-10T12:02:00.000Z", "session_id": "sess_001", "event_type": "environment_switch", "source_app": "VSCode", "target_app": "AWS Console", "environment_id": "env_aws", "metadata": {"dwell_time_ms": 10000}}
    {"timestamp": "2026-08-10T12:05:00.000Z", "session_id": "sess_001", "event_type": "interruption", "source_app": "OS", "metadata": {"is_system_initiated": true}}
    """
    parser = TelemetryParser(dwell_time_threshold_ms=2000.0)
    session = parser.parse_jsonl(jsonl_data)

    assert session.session_id == "sess_001"
    assert len(session.events) == 3
    assert session.duration_minutes == 5.0

    signals = parser.extract_raw_signals(session)

    # 2 qualified environments: env_ide and env_aws
    assert signals["A_raw"] == 2.0
    # 1 context transition over 5 mins = 0.2 transitions / min
    assert signals["S_raw"] == 0.2
    # 1 interruption over 5 mins = 0.2 interruptions / min
    assert signals["I_raw"] == 0.2


def test_dwell_time_threshold_filtering():
    jsonl_data = """
    {"timestamp": "2026-08-10T12:00:00.000Z", "session_id": "sess_002", "event_type": "interaction", "environment_id": "env_main", "metadata": {"dwell_time_ms": 3000}}
    {"timestamp": "2026-08-10T12:01:00.000Z", "session_id": "sess_002", "event_type": "interaction", "environment_id": "env_transient", "metadata": {"dwell_time_ms": 500}}
    """
    parser = TelemetryParser(dwell_time_threshold_ms=2000.0)
    session = parser.parse_jsonl(jsonl_data)
    signals = parser.extract_raw_signals(session)

    # env_transient (500 ms) should be excluded because dwell_time < 2000 ms
    assert signals["A_raw"] == 1.0
