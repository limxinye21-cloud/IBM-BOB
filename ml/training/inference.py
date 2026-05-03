"""
Inference pipeline for AI Packaging Reliability Copilot ML Model
Enhanced with anomaly detection, stage health scores, and better explainability.
"""

import numpy as np
import pandas as pd
import joblib
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


# Per-stage parameter groups for health scoring
STAGE_PARAMS = {
    "die_attach": [
        "die_temperature", "die_epoxy_temperature", "die_void_percentage",
        "die_placement_accuracy", "die_bond_line_thickness", "die_cure_time", "die_pressure",
    ],
    "wire_bonding": [
        "wire_bonding_force", "wire_ultrasonic_power", "wire_loop_height",
        "wire_pull_strength", "wire_bonding_temperature", "wire_diameter", "wire_bond_time",
    ],
    "molding": [
        "mold_temperature", "mold_pressure", "mold_fill_time",
        "mold_compound_viscosity", "mold_transfer_speed", "mold_clamp_force", "mold_voids",
    ],
    "curing": [
        "cure_temperature", "cure_time", "cure_humidity",
        "cure_thermal_profile", "cure_uniformity", "cure_oxygen_level",
    ],
    "inspection": [
        "inspect_defect_count", "inspect_visual_score", "inspect_electrical_test",
        "inspect_reliability_score", "inspect_dimensional_accuracy", "inspect_lead_coplanarity",
    ],
}

# Normal operating ranges for health scoring (min, max)
PARAM_RANGES = {
    "die_temperature": (178, 192),
    "die_epoxy_temperature": (150, 160),
    "die_void_percentage": (0, 3),
    "die_placement_accuracy": (0, 10),
    "die_bond_line_thickness": (22, 28),
    "die_cure_time": (70, 90),
    "die_pressure": (0.6, 1.0),
    "wire_bonding_force": (40, 52),
    "wire_ultrasonic_power": (85, 100),
    "wire_loop_height": (215, 240),
    "wire_pull_strength": (8, 15),
    "wire_bonding_temperature": (160, 170),
    "wire_diameter": (24, 26),
    "wire_bond_time": (18, 24),
    "mold_temperature": (172, 180),
    "mold_pressure": (6.5, 7.8),
    "mold_fill_time": (3.5, 5.0),
    "mold_compound_viscosity": (115, 140),
    "mold_transfer_speed": (11, 14),
    "mold_clamp_force": (55, 68),
    "mold_voids": (0, 1.0),
    "cure_temperature": (178, 184),
    "cure_time": (140, 165),
    "cure_humidity": (35, 50),
    "cure_thermal_profile": (2.5, 3.8),
    "cure_uniformity": (0.5, 2.0),
    "cure_oxygen_level": (0.2, 0.8),
    "inspect_defect_count": (0, 0),
    "inspect_visual_score": (90, 100),
    "inspect_electrical_test": (1, 1),
    "inspect_reliability_score": (92, 100),
    "inspect_dimensional_accuracy": (0, 20),
    "inspect_lead_coplanarity": (30, 50),
}


class ModelInference:
    """
    Inference pipeline for real-time process classification.
    Includes anomaly detection, stage health scoring, and improved explainability.
    """

    def __init__(self, model_dir: str = "ml/saved_models"):
        self.model_dir = Path(model_dir)
        self.model = None
        self.anomaly_detector = None
        self.feature_engineer = None
        self.metadata = None
        self.label_map = None
        self.reverse_label_map = None

    def load_model(self, version: str = "latest"):
        """Load trained model, anomaly detector, and feature engineer."""
        print(f"\n=== Loading Model ===")
        print(f"Model directory: {self.model_dir}")
        print(f"Version: {version}")

        suffix = "latest" if version == "latest" else version
        model_path = self.model_dir / f"model_{suffix}.joblib"
        fe_path = self.model_dir / f"feature_engineer_{suffix}.joblib"
        metadata_path = self.model_dir / f"metadata_{suffix}.json"

        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")
        if not fe_path.exists():
            raise FileNotFoundError(f"Feature engineer not found: {fe_path}")
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata not found: {metadata_path}")

        self.model = joblib.load(model_path)
        print(f"[OK] Model loaded from {model_path}")

        fe_data = joblib.load(fe_path)
        from ml.training.features import FeatureEngineer
        self.feature_engineer = FeatureEngineer()
        self.feature_engineer.scaler = fe_data["scaler"]
        self.feature_engineer.feature_names = fe_data["feature_names"]
        print(f"[OK] Feature engineer loaded from {fe_path}")

        with open(metadata_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)
        print(f"[OK] Metadata loaded from {metadata_path}")

        self.label_map = self.metadata["label_map"]
        self.reverse_label_map = {v: k for k, v in self.label_map.items()}

        # Load anomaly detector (optional — may not exist for old models)
        anomaly_path = self.model_dir / f"anomaly_{suffix}.joblib"
        if anomaly_path.exists():
            self.anomaly_detector = joblib.load(anomaly_path)
            print(f"[OK] Anomaly detector loaded")
        else:
            self.anomaly_detector = None
            print("[--] No anomaly detector found (skipping)")

        print(f"\n[OK] Model ready for inference")
        print(f"  Model type : {self.metadata['model_type']}")
        print(f"  Train acc  : {self.metadata['train_accuracy']:.4f}")
        print(f"  Test acc   : {self.metadata['test_accuracy']:.4f}")
        print(f"  Features   : {self.metadata['n_features']}")
        print(f"  Classes    : {list(self.label_map.keys())}")


    def predict_single(self, data: Dict) -> Dict:
        """Predict status for a single data point, including anomaly score."""
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")

        df = pd.DataFrame([data])
        features = self.feature_engineer.extract_features(df)
        features_scaled = self.feature_engineer.transform(features)

        prediction = self.model.predict(features_scaled)[0]
        probabilities = self.model.predict_proba(features_scaled)[0]
        status = self.reverse_label_map[prediction]

        prob_dict = {
            self.reverse_label_map[i]: float(prob)
            for i, prob in enumerate(probabilities)
        }

        # Anomaly score (higher = more anomalous; -1 to 1 from IsolationForest)
        anomaly_score = None
        if self.anomaly_detector is not None:
            try:
                raw = self.anomaly_detector.score_samples(features_scaled)[0]
                # Normalise to 0–100 (0 = very normal, 100 = very anomalous)
                anomaly_score = float(max(0.0, min(100.0, (-raw + 0.5) * 100)))
            except Exception:
                anomaly_score = None

        return {
            "status": status,
            "confidence": float(probabilities[prediction]),
            "probabilities": prob_dict,
            "prediction_time": datetime.now().isoformat(),
            "feature_values": features.iloc[0].to_dict(),
            "anomaly_score": anomaly_score,
            "stage_health": self.get_stage_health_scores(data),
        }

    def predict_batch(self, data: List[Dict]) -> List[Dict]:
        """Predict status for multiple data points."""
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")

        df = pd.DataFrame(data)
        features = self.feature_engineer.extract_features(df)
        features_scaled = self.feature_engineer.transform(features)

        predictions = self.model.predict(features_scaled)
        probabilities = self.model.predict_proba(features_scaled)

        results = []
        for i, (pred, probs) in enumerate(zip(predictions, probabilities)):
            status = self.reverse_label_map[pred]
            prob_dict = {
                self.reverse_label_map[j]: float(prob)
                for j, prob in enumerate(probs)
            }
            results.append({
                "status": status,
                "confidence": float(probs[pred]),
                "probabilities": prob_dict,
                "prediction_time": datetime.now().isoformat(),
            })

        return results

    def get_stage_health_scores(self, data: Dict) -> Dict[str, float]:
        """
        Compute a 0–100 health score for each process stage.
        100 = all parameters perfectly in range; lower values indicate issues.
        """
        scores = {}
        for stage, params in STAGE_PARAMS.items():
            in_range_count = 0
            total = 0
            for param in params:
                if param not in data:
                    continue
                val = data[param]
                lo, hi = PARAM_RANGES.get(param, (0, 1))
                total += 1
                if lo <= val <= hi:
                    in_range_count += 1
                else:
                    # Partial credit proportional to how far out of range
                    mid = (lo + hi) / 2.0
                    spread = (hi - lo) / 2.0 if hi != lo else 1.0
                    distance = abs(val - np.clip(val, lo, hi))
                    penalty = min(1.0, distance / (spread + 1e-6))
                    in_range_count += max(0.0, 1.0 - penalty)
            scores[stage] = round((in_range_count / total * 100) if total else 100.0, 1)
        return scores

    def explain_prediction(self, data: Dict, top_n: int = 10) -> Dict:
        """
        Explain prediction with feature contributions.
        Uses model feature importances weighted by normalised feature deviation.
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")

        prediction_result = self.predict_single(data)

        df = pd.DataFrame([data])
        features = self.feature_engineer.extract_features(df)
        feature_values = features.iloc[0]
        feature_names = self.feature_engineer.get_feature_importance_names()

        # Extract importances (works for RF, GB, calibrated ensemble)
        importances = self._extract_importances()

        contributions = []
        for name, importance, value in zip(feature_names, importances, feature_values):
            contributions.append({
                "feature": name,
                "value": float(value),
                "importance": float(importance),
                "contribution": float(importance * abs(value)),
            })
        contributions.sort(key=lambda x: x["contribution"], reverse=True)

        return {
            "prediction": prediction_result,
            "top_contributors": contributions[:top_n],
            "explanation_time": datetime.now().isoformat(),
        }

    def _extract_importances(self) -> np.ndarray:
        """Extract feature importances from any supported model architecture."""
        model = self.model
        n_features = len(self.feature_engineer.feature_names)

        # CalibratedClassifierCV
        if hasattr(model, "calibrated_classifiers_"):
            try:
                model = model.calibrated_classifiers_[0].estimator
            except Exception:
                pass

        # VotingClassifier
        if hasattr(model, "estimators_"):
            for sub in model.estimators_:
                if hasattr(sub, "feature_importances_"):
                    return sub.feature_importances_
            return np.ones(n_features) / n_features

        if hasattr(model, "feature_importances_"):
            return model.feature_importances_

        return np.ones(n_features) / n_features

    def get_critical_parameters(self, data: Dict, threshold: float = 0.05) -> List[Dict]:
        """Identify high-importance parameters."""
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")

        importances = self._extract_importances()
        feature_names = self.feature_engineer.get_feature_importance_names()
        df = pd.DataFrame([data])
        features = self.feature_engineer.extract_features(df)
        feature_values = features.iloc[0]

        critical = []
        for name, imp, value in zip(feature_names, importances, feature_values):
            if imp >= threshold:
                critical.append({
                    "parameter": name,
                    "value": float(value),
                    "importance": float(imp),
                    "is_critical": bool(imp >= threshold * 2),
                })
        critical.sort(key=lambda x: x["importance"], reverse=True)
        return critical

    def get_model_info(self) -> Dict:
        """Get model information and metrics."""
        if self.metadata is None:
            raise ValueError("Model not loaded. Call load_model() first.")

        return {
            "model_type": self.metadata["model_type"],
            "training_date": self.metadata["training_date"],
            "n_samples": self.metadata["n_samples"],
            "n_features": self.metadata["n_features"],
            "train_accuracy": self.metadata["train_accuracy"],
            "test_accuracy": self.metadata["test_accuracy"],
            "test_f1": self.metadata.get("test_f1"),
            "roc_auc": self.metadata.get("roc_auc"),
            "cv_mean": self.metadata["cv_mean"],
            "cv_std": self.metadata["cv_std"],
            "classes": list(self.label_map.keys()),
        }


def test_inference():
    """Quick smoke-test of the inference pipeline."""
    print("=" * 70)
    print("INFERENCE PIPELINE TEST")
    print("=" * 70)

    good_data = {
        "die_temperature": 185.0, "die_epoxy_temperature": 155.0, "die_void_percentage": 2.0,
        "die_placement_accuracy": 8.0, "die_bond_line_thickness": 25.0, "die_cure_time": 75.0,
        "die_pressure": 0.8, "wire_bonding_force": 45.0, "wire_ultrasonic_power": 90.0,
        "wire_loop_height": 225.0, "wire_pull_strength": 10.0, "wire_bonding_temperature": 165.0,
        "wire_diameter": 25.0, "wire_bond_time": 20.0, "mold_temperature": 175.0,
        "mold_pressure": 7.0, "mold_fill_time": 4.0, "mold_compound_viscosity": 125.0,
        "mold_transfer_speed": 12.5, "mold_clamp_force": 60.0, "mold_voids": 0.5,
        "cure_temperature": 180.0, "cure_time": 150.0, "cure_humidity": 40.0,
        "cure_thermal_profile": 3.0, "cure_uniformity": 1.5, "cure_oxygen_level": 0.5,
        "inspect_defect_count": 0, "inspect_visual_score": 95.0, "inspect_electrical_test": 1,
        "inspect_reliability_score": 97.0, "inspect_dimensional_accuracy": 15.0,
        "inspect_lead_coplanarity": 40.0,
    }

    try:
        inference = ModelInference()
        inference.load_model(version="latest")

        print("\n=== Model Information ===")
        info = inference.get_model_info()
        for key, value in info.items():
            print(f"  {key}: {value}")

        print("\n=== Single Prediction ===")
        result = inference.predict_single(good_data)
        print(f"  Status    : {result['status']}")
        print(f"  Confidence: {result['confidence']:.4f}")
        print(f"  Anomaly   : {result.get('anomaly_score')}")
        print(f"  Probabilities:")
        for status, prob in result["probabilities"].items():
            print(f"    {status}: {prob:.4f}")

        print("\n=== Stage Health Scores ===")
        for stage, score in result.get("stage_health", {}).items():
            print(f"  {stage:15s}: {score:.1f}/100")

        print("\n=== Prediction Explanation (top 5) ===")
        explanation = inference.explain_prediction(good_data, top_n=5)
        for contrib in explanation["top_contributors"]:
            print(f"  {contrib['feature']:40s} importance={contrib['importance']:.4f}")
        for param in critical[:5]:
            print(f"  {param['parameter']:40s} importance={param['importance']:.4f}")
        
        print("\n✓ Inference test complete")
        
    except FileNotFoundError as e:
        print(f"\n⚠ Model not found: {e}")
        print("Please run training first: python ml/training/train.py")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_inference()

# Made with Bob
