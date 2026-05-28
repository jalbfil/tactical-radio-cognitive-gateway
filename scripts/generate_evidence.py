from __future__ import annotations
import json
from pathlib import Path
from tactical_radio_gateway.data_generator import generate_window
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data' / 'sample_windows'
def main() -> None:
    for scenario in ['nominal', 'degraded_climate', 'jammed_attack']:
        scenario_dir = OUT / scenario; scenario_dir.mkdir(parents=True, exist_ok=True)
        payload = [item.model_dump() for item in generate_window(scenario, samples=12, seed=42)]
        (scenario_dir / 'window.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')
        print(f'Generated {scenario_dir / "window.json"}')
if __name__ == '__main__': main()
