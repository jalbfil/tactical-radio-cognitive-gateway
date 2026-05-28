from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
import numpy as np
from tactical_radio_gateway.schemas import LinkState, RadioMetrics

@dataclass(frozen=True)
class ScenarioProfile:
    label: LinkState
    rssi_mean: float; rssi_std: float
    snr_mean: float; snr_std: float
    packet_loss_mean: float; packet_loss_std: float
    rtt_mean: float; rtt_std: float
    jitter_mean: float; jitter_std: float
    occupancy_mean: float; occupancy_std: float

PROFILES = {
    "nominal": ScenarioProfile(LinkState.NOMINAL, -58,4, 27,3, 1.2,0.8, 42,7, 5,2, 35,8),
    "degraded_climate": ScenarioProfile(LinkState.DEGRADED_CLIMATE, -88,6, 11,3, 13,4, 92,15, 18,6, 42,9),
    "jammed_attack": ScenarioProfile(LinkState.JAMMED_ATTACK, -46,5, 2.5,1.8, 38,9, 185,35, 55,14, 92,6),
}
FEATURE_NAMES = ["rssi_dbm","snr_db","packet_loss_pct","rtt_ms","jitter_ms","channel_occupancy_pct"]

def _clip(values: dict[str,float]) -> dict[str,float]:
    values["rssi_dbm"] = float(np.clip(values["rssi_dbm"], -115, -25))
    values["snr_db"] = float(np.clip(values["snr_db"], -5, 40))
    values["packet_loss_pct"] = float(np.clip(values["packet_loss_pct"], 0, 100))
    values["rtt_ms"] = float(np.clip(values["rtt_ms"], 10, 500))
    values["jitter_ms"] = float(np.clip(values["jitter_ms"], 0, 200))
    values["channel_occupancy_pct"] = float(np.clip(values["channel_occupancy_pct"], 0, 100))
    return values

def generate_metric(profile: ScenarioProfile, rng: np.random.Generator) -> RadioMetrics:
    return RadioMetrics(**_clip({
        "rssi_dbm": rng.normal(profile.rssi_mean, profile.rssi_std),
        "snr_db": rng.normal(profile.snr_mean, profile.snr_std),
        "packet_loss_pct": rng.normal(profile.packet_loss_mean, profile.packet_loss_std),
        "rtt_ms": rng.normal(profile.rtt_mean, profile.rtt_std),
        "jitter_ms": rng.normal(profile.jitter_mean, profile.jitter_std),
        "channel_occupancy_pct": rng.normal(profile.occupancy_mean, profile.occupancy_std),
    }))

def generate_window(scenario: str, samples: int = 12, seed: int | None = None) -> list[RadioMetrics]:
    if scenario not in PROFILES:
        raise ValueError(f"Unknown scenario: {scenario}")
    rng=np.random.default_rng(seed); profile=PROFILES[scenario]
    return [generate_metric(profile, rng) for _ in range(samples)]

def window_to_features(window: Iterable[RadioMetrics]) -> list[float]:
    items=list(window)
    if not items: raise ValueError("A metric window must contain at least one sample")
    arr=np.array([[getattr(item,n) for n in FEATURE_NAMES] for item in items], dtype=float)
    return [*arr.mean(axis=0).tolist(), *arr.std(axis=0).tolist()]

def build_training_dataset(samples_per_class:int=500, window_size:int=12, seed:int=42):
    rng=np.random.default_rng(seed); x=[]; y=[]
    for scenario, profile in PROFILES.items():
        for _ in range(samples_per_class):
            window=generate_window(scenario, samples=window_size, seed=int(rng.integers(0,1_000_000)))
            x.append(window_to_features(window)); y.append(profile.label.value)
    return np.array(x,dtype=float), np.array(y,dtype=str)

def average_metrics(window: Iterable[RadioMetrics]) -> RadioMetrics:
    items=list(window)
    arr=np.array([[getattr(item,n) for n in FEATURE_NAMES] for item in items], dtype=float)
    return RadioMetrics(**{n: float(v) for n,v in zip(FEATURE_NAMES, arr.mean(axis=0))})
