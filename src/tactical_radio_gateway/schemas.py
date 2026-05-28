from __future__ import annotations
from enum import Enum
from pydantic import BaseModel, Field

class LinkState(str, Enum):
    NOMINAL = "NOMINAL"
    DEGRADED_CLIMATE = "DEGRADED_CLIMATE"
    JAMMED_ATTACK = "JAMMED_ATTACK"

class RouteMode(str, Enum):
    UHF_PRIMARY = "UHF_PRIMARY"
    UHF_COMPRESSED = "UHF_COMPRESSED"
    SATCOM_FALLBACK = "SATCOM_FALLBACK"

class RadioMetrics(BaseModel):
    rssi_dbm: float = Field(description="Received signal strength indicator in dBm")
    snr_db: float = Field(description="Signal-to-noise ratio in dB")
    packet_loss_pct: float = Field(description="Packet loss percentage")
    rtt_ms: float = Field(description="Round trip time in milliseconds")
    jitter_ms: float = Field(description="Jitter in milliseconds")
    channel_occupancy_pct: float = Field(description="Synthetic spectrum/channel occupancy percentage")

class ClassificationResult(BaseModel):
    state: LinkState
    confidence: float
    features: RadioMetrics

class GatewayDecision(BaseModel):
    route_mode: RouteMode
    uhf_enabled: bool
    satcom_enabled: bool
    compression_enabled: bool
    compression_level: str
    critical_traffic_only: bool
    ew_alarm: bool
    operator_message: str
    recommended_action: str

class GatewayStatus(BaseModel):
    scenario: str
    classification: ClassificationResult
    decision: GatewayDecision
    topology: dict
