from tactical_radio_gateway.data_generator import generate_window, window_to_features

def test_generate_window_has_expected_size():
    window = generate_window('nominal', samples=12, seed=1)
    assert len(window) == 12

def test_window_to_features_contains_means_and_stds():
    window = generate_window('nominal', samples=12, seed=1)
    features = window_to_features(window)
    assert len(features) == 12
