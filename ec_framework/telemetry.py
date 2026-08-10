"""
Telemetry protocol and raw candidate signal extraction for MF-0.1 (v0.2).

Note on Epistemic Boundaries:
Telemetry extraction produces *candidate raw signals* (A_raw, S_raw, I_raw).
These raw counts are NOT baseline-adjusted measurements or validated Ec scores;
they represent uncalibrated telemetry inputs to be processed in later phases.
"""

from dataclasses import dataclass, field
from datetime import datetime
import json
from typing import List, Dict, Any, Optional


@dataclass
class TelemetryEvent:
    """A single raw interaction telemetry event log entry."""
    timestamp: str
    session_id: str
    event_type: str  # e.g., 'environment_switch', 'interaction', 'interruption', 'decision'
    source_app: str = ""
    target_app: str = ""
    environment_id: str = ""
    action: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TelemetryEvent":
        return cls(
            timestamp=data.get("timestamp", ""),
            session_id=data.get("session_id", ""),
            event_type=data.get("event_type", ""),
            source_app=data.get("source_app", ""),
            target_app=data.get("target_app", ""),
            environment_id=data.get("environment_id", ""),
            action=data.get("action", ""),
            metadata=data.get("metadata", {}),
        )


@dataclass
class InteractionSession:
    """A sequence of telemetry events belonging to a single continuous task session."""
    session_id: str
    events: List[TelemetryEvent] = field(default_factory=list)

    @property
    def duration_seconds(self) -> float:
        """Calculates total session duration in seconds based on first and last event timestamps."""
        if len(self.events) < 2:
            return 0.0
        try:
            t0 = datetime.fromisoformat(self.events[0].timestamp.replace("Z", "+00:00"))
            t1 = datetime.fromisoformat(self.events[-1].timestamp.replace("Z", "+00:00"))
            return max(0.0, (t1 - t0).total_seconds())
        except (ValueError, TypeError):
            return 0.0

    @property
    def duration_minutes(self) -> float:
        return self.duration_seconds / 60.0


class TelemetryParser:
    """Parses telemetry logs and extracts candidate raw signals.
    
    Default parameters follow spec addendum v0.2:
      - dwell_time_threshold_ms: minimum dwell time to qualify an environment context (2000 ms)
    """

    def __init__(self, dwell_time_threshold_ms: float = 2000.0):
        self.dwell_time_threshold_ms = dwell_time_threshold_ms

    def parse_line(self, line: str) -> Optional[TelemetryEvent]:
        """Parses a single JSON line into a TelemetryEvent."""
        line = line.strip()
        if not line or line.startswith("#"):
            return None
        data = json.loads(line)
        return TelemetryEvent.from_dict(data)

    def parse_jsonl(self, jsonl_content: str) -> InteractionSession:
        """Parses a full multi-line JSONL string into an InteractionSession."""
        events = []
        session_id = "unknown_session"
        for line in jsonl_content.splitlines():
            evt = self.parse_line(line)
            if evt:
                events.append(evt)
                if evt.session_id:
                    session_id = evt.session_id

        return InteractionSession(session_id=session_id, events=events)

    def extract_raw_signals(self, session: InteractionSession) -> Dict[str, float]:
        """Extracts candidate raw signals from an interaction session:
        
        - A_raw: Count of distinct environments visited with dwell_time >= threshold_ms
        - S_raw: Context transition rate per minute (transitions / min)
        - I_raw: System-initiated interruption rate per minute (interruptions / min)
        """
        if not session.events:
            return {"A_raw": 0.0, "S_raw": 0.0, "I_raw": 0.0}

        # 1. Application Fragmentation (A_raw): Unique qualified environments
        environments = set()
        for evt in session.events:
            env = evt.environment_id or (evt.target_app if evt.event_type == "environment_switch" else None)
            if env:
                dwell_time = evt.metadata.get("dwell_time_ms", 0.0)
                # Count if dwell_time >= threshold or if dwell time is unspecified (default to include)
                if dwell_time >= self.dwell_time_threshold_ms or "dwell_time_ms" not in evt.metadata:
                    environments.add(env)

        a_raw = float(len(environments))

        # 2. Context Transitions (S_raw): Count environment_switch events
        transition_count = 0
        for evt in session.events:
            if evt.event_type == "environment_switch":
                # Only count transitions between different apps/environments
                if evt.source_app and evt.target_app and evt.source_app != evt.target_app:
                    transition_count += 1

        duration_min = session.duration_minutes
        s_raw = (transition_count / duration_min) if duration_min > 0 else 0.0

        # 3. Interruptions (I_raw): Count system-initiated interruptions
        interruption_count = 0
        for evt in session.events:
            if evt.event_type == "interruption" or evt.metadata.get("is_system_initiated", False):
                interruption_count += 1

        i_raw = (interruption_count / duration_min) if duration_min > 0 else 0.0

        return {
            "A_raw": a_raw,
            "S_raw": s_raw,
            "I_raw": i_raw,
            "session_duration_min": duration_min,
            "total_event_count": float(len(session.events)),
        }
