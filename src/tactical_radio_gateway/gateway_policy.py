from tactical_radio_gateway.schemas import GatewayDecision, LinkState, RouteMode

def decide_gateway_policy(state: LinkState) -> GatewayDecision:
    if state == LinkState.NOMINAL:
        return GatewayDecision(route_mode=RouteMode.UHF_PRIMARY, uhf_enabled=True, satcom_enabled=False, compression_enabled=False, compression_level="none", critical_traffic_only=False, ew_alarm=False, operator_message="UHF primary link is healthy. Normal mission data flow is allowed.", recommended_action="Continue monitoring channel health.")
    if state == LinkState.DEGRADED_CLIMATE:
        return GatewayDecision(route_mode=RouteMode.UHF_COMPRESSED, uhf_enabled=True, satcom_enabled=False, compression_enabled=True, compression_level="medium", critical_traffic_only=False, ew_alarm=False, operator_message="UHF link degraded by attenuation-like conditions. Compression and rate control enabled.", recommended_action="Maintain UHF path, reduce non-essential bandwidth and monitor trend.")
    if state == LinkState.JAMMED_ATTACK:
        return GatewayDecision(route_mode=RouteMode.SATCOM_FALLBACK, uhf_enabled=False, satcom_enabled=True, compression_enabled=True, compression_level="aggressive", critical_traffic_only=True, ew_alarm=True, operator_message="Synthetic EW jamming pattern detected. Critical traffic is routed through SATCOM fallback.", recommended_action="Protect critical traces, suppress secondary flows and keep monitoring recovery conditions.")
    raise ValueError(f"Unsupported state: {state}")
