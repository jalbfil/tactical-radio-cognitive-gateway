from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from tactical_radio_gateway.gateway_policy import decide_gateway_policy
from tactical_radio_gateway.ml_classifier import classify_window
from tactical_radio_gateway.schemas import GatewayStatus


SCENARIO_ALIASES = {
    "nominal": "nominal",
    "degraded": "degraded_climate",
    "climate": "degraded_climate",
    "degraded_climate": "degraded_climate",
    "jammed": "jammed_attack",
    "attack": "jammed_attack",
    "jammed_attack": "jammed_attack",
}

PLAYBACK_SEQUENCE = ["nominal", "degraded_climate", "jammed_attack"]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalize_scenario(name: str) -> str:
    try:
        return SCENARIO_ALIASES[name.lower()]
    except KeyError as exc:
        allowed = ", ".join(sorted(SCENARIO_ALIASES))
        raise ValueError(f"Unknown scenario '{name}'. Allowed values: {allowed}") from exc


def topology_for_state(state_name: str) -> dict[str, Any]:
    if state_name == "NOMINAL":
        statuses = ("green", "green", "standby")
    elif state_name == "DEGRADED_CLIMATE":
        statuses = ("yellow", "yellow", "standby")
    else:
        statuses = ("red", "red", "green")

    return {
        "nodes": [
            {"id": "BASE", "label": "BASE", "role": "Ground command post"},
            {"id": "UAV-01", "label": "UAV-01", "role": "Unmanned relay/support node"},
            {"id": "AIR-01", "label": "AIR-01", "role": "Crewed airborne platform"},
        ],
        "links": [
            {"id": "BASE-UAV", "from": "BASE", "to": "UAV-01", "type": "UHF", "status": statuses[0]},
            {"id": "UAV-AIR", "from": "UAV-01", "to": "AIR-01", "type": "UHF", "status": statuses[1]},
            {"id": "BASE-AIR-SATCOM", "from": "BASE", "to": "AIR-01", "type": "SATCOM", "status": statuses[2]},
        ],
    }


@dataclass
class GatewayRuntimeState:
    scenario: str = "nominal"
    tick_counter: int = 0
    history_limit: int = 40
    _history: list[dict[str, Any]] = field(default_factory=list)

    def _build_status(self, *, seed: int | None = None) -> GatewayStatus:
        effective_seed = seed if seed is not None else 1000 + self.tick_counter
        classification = classify_window(self.scenario, seed=effective_seed)
        decision = decide_gateway_policy(classification.state)
        return GatewayStatus(
            scenario=self.scenario,
            classification=classification,
            decision=decision,
            topology=topology_for_state(classification.state.value),
        )

    def _history_item(self, status: GatewayStatus) -> dict[str, Any]:
        features = status.classification.features
        return {
            "timestamp": utc_now_iso(),
            "tick": self.tick_counter,
            "scenario": status.scenario,
            "state": status.classification.state.value,
            "confidence": round(status.classification.confidence, 4),
            "route_mode": status.decision.route_mode.value,
            "ew_alarm": status.decision.ew_alarm,
            "metrics": {
                "rssi_dbm": round(features.rssi_dbm, 2),
                "snr_db": round(features.snr_db, 2),
                "packet_loss_pct": round(features.packet_loss_pct, 2),
                "rtt_ms": round(features.rtt_ms, 2),
                "jitter_ms": round(features.jitter_ms, 2),
                "channel_occupancy_pct": round(features.channel_occupancy_pct, 2),
            },
        }

    def _record(self, status: GatewayStatus) -> None:
        self._history.append(self._history_item(status))
        if len(self._history) > self.history_limit:
            self._history = self._history[-self.history_limit :]

    def set_scenario(self, scenario: str) -> GatewayStatus:
        self.scenario = normalize_scenario(scenario)
        self.tick_counter = 0
        status = self._build_status()
        self._record(status)
        return status

    def current_status(self) -> GatewayStatus:
        return self._build_status()

    def tick(self) -> GatewayStatus:
        self.tick_counter += 1
        status = self._build_status()
        self._record(status)
        return status

    def history(self) -> list[dict[str, Any]]:
        return list(self._history)

    def export_report(self) -> dict[str, Any]:
        status = self.current_status()
        features = status.classification.features
        return {
            "report_type": "tactical-radio-cognitive-gateway",
            "generated_at": utc_now_iso(),
            "scenario": status.scenario,
            "classification": {
                "state": status.classification.state.value,
                "confidence": round(status.classification.confidence, 4),
            },
            "gateway_decision": {
                "route_mode": status.decision.route_mode.value,
                "uhf_enabled": status.decision.uhf_enabled,
                "satcom_enabled": status.decision.satcom_enabled,
                "compression_enabled": status.decision.compression_enabled,
                "compression_level": status.decision.compression_level,
                "critical_traffic_only": status.decision.critical_traffic_only,
                "ew_alarm": status.decision.ew_alarm,
                "operator_message": status.decision.operator_message,
                "recommended_action": status.decision.recommended_action,
            },
            "metrics": {
                "rssi_dbm": round(features.rssi_dbm, 2),
                "snr_db": round(features.snr_db, 2),
                "packet_loss_pct": round(features.packet_loss_pct, 2),
                "rtt_ms": round(features.rtt_ms, 2),
                "jitter_ms": round(features.jitter_ms, 2),
                "channel_occupancy_pct": round(features.channel_occupancy_pct, 2),
            },
            "topology": status.topology,
            "safety_note": "Synthetic defensive lab. No real RF control, jamming technique or operational EW capability is implemented.",
        }

    def playback(self) -> list[GatewayStatus]:
        self._history.clear()
        results: list[GatewayStatus] = []

        for index, scenario in enumerate(PLAYBACK_SEQUENCE):
            self.scenario = scenario
            self.tick_counter = index + 1
            status = self._build_status(seed=3000 + index)
            self._record(status)
            results.append(status)

        return results
