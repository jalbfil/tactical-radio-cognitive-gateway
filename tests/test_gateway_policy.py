from tactical_radio_gateway.gateway_policy import decide_gateway_policy
from tactical_radio_gateway.schemas import LinkState, RouteMode

def test_nominal_policy_uses_uhf_primary():
    decision = decide_gateway_policy(LinkState.NOMINAL)
    assert decision.route_mode == RouteMode.UHF_PRIMARY
    assert decision.ew_alarm is False

def test_jammed_policy_uses_satcom_and_alarm():
    decision = decide_gateway_policy(LinkState.JAMMED_ATTACK)
    assert decision.route_mode == RouteMode.SATCOM_FALLBACK
    assert decision.satcom_enabled is True
    assert decision.ew_alarm is True
