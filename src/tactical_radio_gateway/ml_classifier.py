from __future__ import annotations
from functools import lru_cache
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from tactical_radio_gateway.data_generator import average_metrics, build_training_dataset, generate_window, window_to_features
from tactical_radio_gateway.schemas import ClassificationResult, LinkState

def train_classifier(seed:int=42) -> Pipeline:
    x_train, y_train = build_training_dataset(samples_per_class=450, window_size=12, seed=seed)
    model = Pipeline([("scaler", StandardScaler()), ("clf", RandomForestClassifier(n_estimators=120, max_depth=8, random_state=seed, class_weight="balanced"))])
    model.fit(x_train, y_train); return model

@lru_cache(maxsize=1)
def get_classifier() -> Pipeline:
    return train_classifier(seed=42)

def classify_window(scenario: str, seed: int | None = None) -> ClassificationResult:
    window=generate_window(scenario, samples=12, seed=seed)
    return classify_metrics(window)

def classify_metrics(window) -> ClassificationResult:
    model=get_classifier(); features=np.array([window_to_features(window)], dtype=float)
    label=str(model.predict(features)[0]); confidence=1.0
    if hasattr(model, "predict_proba"):
        probs=model.predict_proba(features)[0]; classes=list(model.classes_); confidence=float(probs[classes.index(label)])
    return ClassificationResult(state=LinkState(label), confidence=confidence, features=average_metrics(window))
