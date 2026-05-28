from dataclasses import dataclass
from tactical_radio_gateway.gateway_policy import decide_gateway_policy
from tactical_radio_gateway.ml_classifier import classify_window
from tactical_radio_gateway.schemas import GatewayStatus

SCENARIO_ALIASES={"nominal":"nominal","degraded":"degraded_climate","climate":"degraded_climate","degraded_climate":"degraded_climate","jammed":"jammed_attack","attack":"jammed_attack","jammed_attack":"jammed_attack"}

def normalize_scenario(name:str)->str:
    try: return SCENARIO_ALIASES[name.lower()]
    except KeyError as exc: raise ValueError(f"Unknown scenario '{name}'") from exc

def topology_for_state(state_name:str):
    if state_name == "NOMINAL":
        statuses=("green","green","standby")
    elif state_name == "DEGRADED_CLIMATE":
        statuses=("yellow","yellow","standby")
    else:
        statuses=("red","red","green")
    return {"nodes":[{"id":"BASE","label":"BASE","role":"Ground command post"},{"id":"UAV-01","label":"UAV-01","role":"Unmanned relay/support node"},{"id":"AIR-01","label":"AIR-01","role":"Crewed airborne platform"}], "links":[{"id":"BASE-UAV","from":"BASE","to":"UAV-01","type":"UHF","status":statuses[0]},{"id":"UAV-AIR","from":"UAV-01","to":"AIR-01","type":"UHF","status":statuses[1]},{"id":"BASE-AIR-SATCOM","from":"BASE","to":"AIR-01","type":"SATCOM","status":statuses[2]}]}

@dataclass
class GatewayRuntimeState:
    scenario: str = "nominal"
    tick_counter: int = 0
    def set_scenario(self, scenario: str) -> GatewayStatus:
        self.scenario=normalize_scenario(scenario); self.tick_counter=0; return self.current_status()
    def current_status(self) -> GatewayStatus:
        c=classify_window(self.scenario, seed=1000+self.tick_counter); d=decide_gateway_policy(c.state)
        return GatewayStatus(scenario=self.scenario, classification=c, decision=d, topology=topology_for_state(c.state.value))
    def tick(self) -> GatewayStatus:
        self.tick_counter += 1; return self.current_status()
