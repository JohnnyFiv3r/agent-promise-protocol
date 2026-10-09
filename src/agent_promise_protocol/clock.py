"""Clock integration points. Production must supply authenticated uncertainty evidence."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ClockReading:
    now_ms: int
    uncertainty_ms: int
    evidence_ref: dict


class ControlledClock:
    """Explicit deterministic test clock; never advertised as an NTS integration."""

    def __init__(self, now_ms, evidence_ref, uncertainty_ms=0):
        self.now_ms = now_ms
        self.evidence_ref = evidence_ref
        self.uncertainty_ms = uncertainty_ms

    def read(self):
        return ClockReading(self.now_ms, self.uncertainty_ms, self.evidence_ref)

    def advance(self, milliseconds):
        if milliseconds < 0:
            raise ValueError("controlled time cannot move backwards")
        self.now_ms += milliseconds
