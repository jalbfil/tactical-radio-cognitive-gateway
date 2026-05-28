# Tactical Radio Cognitive Gateway

Lightweight, synthetic and defensive lab for radio-link health classification and dynamic communications fallback.

This repository continues the previous portfolio line:

1. [`tactical-ospf-resilience-lab`](https://github.com/jalbfil/tactical-ospf-resilience-lab) — manual validation of an OSPF-resilient tactical IP topology.
2. [`tactical-netdevops-validator`](https://github.com/jalbfil/tactical-netdevops-validator) — automated classification of network state.
3. [`tactical-c2-network-dashboard`](https://github.com/jalbfil/tactical-c2-network-dashboard) — C2-inspired visualization of network state.

This fourth project adds a cognitive gateway concept: synthetic radio-link metrics, a local ML classifier and a policy engine that decides how to route mission data when the primary UHF link degrades.

> This is a controlled educational lab. It does not implement real electronic warfare, jamming techniques, RF control, operational frequencies, or deployable military communications. It uses synthetic metrics to demonstrate defensive resilience, edge classification and operator visualization.

---

## 1. Scenario

```text
BASE  <---- UHF primary link ---->  UAV-01  <---- UHF relay ---->  AIR-01
  \                                                                  /
   \------------------ SATCOM fallback, narrowband -----------------/
```

- `BASE`: ground command post.
- `UAV-01`: unmanned relay/support element.
- `AIR-01`: crewed airborne platform.
- `UHF`: primary tactical radio link, higher capacity but vulnerable to degradation/interference.
- `SATCOM`: backup link, lower capacity but used for critical traffic during severe disruption.

---

## 2. Problem

A traditional network check may only see that the link is failing. It does not explain why.

This lab separates two different causes:

| State | Meaning | Typical metric behavior |
|---|---|---|
| `NOMINAL` | Healthy primary UHF channel | Good RSSI, high SNR, low loss |
| `DEGRADED_CLIMATE` | Natural attenuation / distance / weather-like degradation | RSSI decreases and SNR decreases proportionally |
| `JAMMED_ATTACK` | Synthetic active interference pattern | RSSI remains high or rises, but SNR collapses and packet loss spikes |

The important learning point:

> In a jammed-like synthetic pattern, received power may be high because the receiver sees more energy, but the useful signal quality collapses because noise dominates the channel.

---

## 3. What the project does

The MVP includes:

- Synthetic radio evidence generator.
- Local ML classifier with Scikit-Learn.
- Gateway decision policy.
- FastAPI backend.
- HTML/CSS/JavaScript dashboard.
- Scenario selector: `Nominal`, `Climate / distance degradation`, `Jammed / attack pattern`.
- API endpoints for metrics, classification and policy.
- Tests with `pytest`.
- Documentation and LinkedIn-ready brief.

---

## 4. Classifier states

### `NOMINAL`

Primary UHF link is healthy.

Gateway decision:

```text
Keep UHF as primary path.
No compression required.
No EW alarm.
```

### `DEGRADED_CLIMATE`

The UHF channel is degraded but still usable.

Gateway decision:

```text
Keep UHF path.
Enable compression.
Reduce data rate.
Prioritize essential telemetry.
```

### `JAMMED_ATTACK`

The primary channel presents a synthetic active interference pattern.

Gateway decision:

```text
Raise EW alarm.
Cut non-critical flow.
Route critical traces through SATCOM fallback.
Enable aggressive compression.
```

---

## 5. Architecture

```text
Synthetic radio metrics
        ↓
Feature window
        ↓
Local ML classifier
        ↓
Gateway policy engine
        ↓
FastAPI API
        ↓
C2-inspired dashboard
```

---

## 6. Installation

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

or:

```bash
pip install -e .[dev]
```

---

## 7. Run tests

```bash
pytest -q
```

---

## 8. Run the dashboard

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

---

## 9. API examples

```bash
curl http://127.0.0.1:8000/api/status
curl -X POST http://127.0.0.1:8000/api/scenario/nominal
curl -X POST http://127.0.0.1:8000/api/scenario/degraded_climate
curl -X POST http://127.0.0.1:8000/api/scenario/jammed_attack
curl -X POST http://127.0.0.1:8000/api/tick
```

---

## 10. Repository structure

```text
tactical-radio-cognitive-gateway/
├── README.md
├── pyproject.toml
├── requirements.txt
├── .env.example
├── app/
│   ├── main.py
│   └── static/
├── src/tactical_radio_gateway/
├── scripts/
├── data/sample_windows/
├── docs/
├── tests/
├── assets/
└── linkedin/
```

---

## 11. Professional value

This project demonstrates:

- Telecommunications and radio-link reasoning.
- Defensive resilience against degraded communications.
- Local ML applied to edge-style classification.
- Lightweight gateway decision logic.
- FastAPI backend development.
- C2/CIS-inspired visualization.
- End-to-end thinking: signal metrics → ML diagnosis → routing policy → operator view.

The practical idea is:

> In critical communications, it is not enough to know that a link is failing. It is more useful to infer why it is failing and adapt the routing policy accordingly.
