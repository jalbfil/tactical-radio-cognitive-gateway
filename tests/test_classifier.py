from tactical_radio_gateway.ml_classifier import classify_window

def test_nominal_classification():
    assert classify_window('nominal', seed=10).state.value == 'NOMINAL'

def test_degraded_classification():
    assert classify_window('degraded_climate', seed=10).state.value == 'DEGRADED_CLIMATE'

def test_jammed_classification():
    assert classify_window('jammed_attack', seed=10).state.value == 'JAMMED_ATTACK'
