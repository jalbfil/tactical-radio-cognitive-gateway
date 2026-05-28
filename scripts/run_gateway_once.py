from tactical_radio_gateway.gateway_policy import decide_gateway_policy
from tactical_radio_gateway.ml_classifier import classify_window

def main() -> None:
    for scenario in ['nominal', 'degraded_climate', 'jammed_attack']:
        result = classify_window(scenario, seed=42)
        decision = decide_gateway_policy(result.state)
        print(f'{scenario}: {result.state.value} confidence={result.confidence:.2f} route={decision.route_mode.value}')
if __name__ == '__main__': main()
