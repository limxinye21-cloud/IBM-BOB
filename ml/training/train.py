"""
Training pipeline for AI Packaging Reliability Copilot ML Model
Enhanced with Gradient Boosting ensemble + anomaly detection
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    VotingClassifier,
    IsolationForest,
)
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    f1_score,
    roc_auc_score,
)
import joblib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from ml.training.features import FeatureEngineer, prepare_labels
from data.mock.generator import MockDataGenerator
from data.mock.scenarios import SCENARIOS


class ModelTrainer:
    """
    Training pipeline for process classification model.
    Uses a calibrated VotingClassifier (RF + GB) ensemble for best accuracy,
    plus an IsolationForest for unsupervised anomaly detection.
    """

    def __init__(
        self,
        model_type: str = "ensemble",
        random_state: int = 42,
    ):
        """
        Initialize model trainer.

        Args:
            model_type: "ensemble" (RF + GB voting), "random_forest", or "gradient_boosting"
            random_state: Random seed for reproducibility
        """
        self.model_type = model_type
        self.random_state = random_state
        self.model = None
        self.anomaly_detector = None
        self.feature_engineer = FeatureEngineer()
        self.label_map = None
        self.training_metadata = {}

    def create_model(self):
        """
        Create the classification model.

        Returns:
            Initialized (and optionally calibrated) model
        """
        if self.model_type == "ensemble":
            rf = RandomForestClassifier(
                n_estimators=200,
                max_depth=12,
                min_samples_split=4,
                min_samples_leaf=2,
                max_features="sqrt",
                random_state=self.random_state,
                n_jobs=-1,
                class_weight="balanced",
            )
            gb = GradientBoostingClassifier(
                n_estimators=150,
                learning_rate=0.08,
                max_depth=5,
                min_samples_split=4,
                min_samples_leaf=2,
                subsample=0.85,
                random_state=self.random_state,
            )
            model = VotingClassifier(
                estimators=[("rf", rf), ("gb", gb)],
                voting="soft",
                weights=[1, 1],
                n_jobs=-1,
            )
            # Calibrate for reliable probability estimates
            model = CalibratedClassifierCV(model, cv=3, method="isotonic")

        elif self.model_type == "random_forest":
            model = RandomForestClassifier(
                n_estimators=200,
                max_depth=12,
                min_samples_split=4,
                min_samples_leaf=2,
                max_features="sqrt",
                random_state=self.random_state,
                n_jobs=-1,
                class_weight="balanced",
            )

        elif self.model_type == "gradient_boosting":
            model = GradientBoostingClassifier(
                n_estimators=200,
                learning_rate=0.08,
                max_depth=5,
                subsample=0.85,
                random_state=self.random_state,
            )

        else:
            raise ValueError(f"Unknown model type: {self.model_type}")

        return model

    def create_anomaly_detector(self) -> IsolationForest:
        """Create IsolationForest for unsupervised anomaly detection."""
        return IsolationForest(
            n_estimators=100,
            contamination=0.1,
            random_state=self.random_state,
            n_jobs=-1,
        )
    
    def generate_training_data(
        self,
        n_samples: int = 20000,
        include_scenarios: bool = True,
    ) -> pd.DataFrame:
        """
        Generate training data using mock data generator.
        Generates 20k samples by default for a stronger model.
        """
        print(f"\n=== Generating Training Data ===")
        print(f"Target samples: {n_samples}")

        generator = MockDataGenerator()
        all_data = []

        # Normal operation data (55%)
        normal_samples = int(n_samples * 0.55)
        print(f"Generating {normal_samples} normal samples...")
        for _ in range(normal_samples):
            data = generator.generate_single()
            all_data.append(data)

        # Scenario-based data (45%)
        if include_scenarios:
            scenario_samples = n_samples - normal_samples
            samples_per_scenario = scenario_samples // len(SCENARIOS)

            print(f"Generating {scenario_samples} scenario-based samples...")
            for scenario_name, scenario_config in SCENARIOS.items():
                print(f"  - {scenario_name}: {samples_per_scenario} samples")
                for _ in range(samples_per_scenario):
                    data = generator.generate_single(scenario=scenario_config)
                    all_data.append(data)

        df = pd.DataFrame(all_data)

        status_dist = df["status"].value_counts()
        print(f"\n[OK] Generated {len(df)} samples")
        print(f"  Status distribution:")
        for status, count in status_dist.items():
            print(f"    {status}: {count} ({count/len(df)*100:.1f}%)")

        return df
    
    def train(
        self,
        data: pd.DataFrame,
        test_size: float = 0.2,
        validation_split: float = 0.1,
    ) -> Dict:
        """
        Train the model with cross-validation, F1, and ROC-AUC reporting.

        Args:
            data: Training data
            test_size: Test set size fraction
            validation_split: Validation set size fraction

        Returns:
            Training results dictionary
        """
        print(f"\n=== Training Model ===")
        print(f"Model type: {self.model_type}")
        print(f"Total samples: {len(data)}")

        # Extract features
        print("\nExtracting features...")
        features = self.feature_engineer.extract_features(data)
        print(f"[OK] Extracted {len(features.columns)} features")

        # Prepare labels
        labels, self.label_map = prepare_labels(data)
        print(f"[OK] Prepared labels with {len(self.label_map)} classes")

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            features,
            labels,
            test_size=test_size,
            random_state=self.random_state,
            stratify=labels,
        )

        print(f"\n[OK] Data split:")
        print(f"  Training: {len(X_train)} samples")
        print(f"  Testing:  {len(X_test)} samples")

        # Scale features
        print("\nScaling features...")
        X_train_scaled = self.feature_engineer.fit_transform(X_train)
        X_test_scaled = self.feature_engineer.transform(X_test)
        print("[OK] Features scaled")

        # Train anomaly detector on GOOD-only data
        print("\nTraining anomaly detector (IsolationForest)...")
        self.anomaly_detector = self.create_anomaly_detector()
        good_idx = y_train == self.label_map.get("GOOD", 0)
        self.anomaly_detector.fit(X_train_scaled[good_idx])
        print("[OK] Anomaly detector trained")

        # Train main classifier
        print(f"\nTraining {self.model_type} classifier...")
        self.model = self.create_model()
        self.model.fit(X_train_scaled, y_train)
        print("[OK] Classifier trained")

        # Evaluate
        train_pred = self.model.predict(X_train_scaled)
        train_accuracy = accuracy_score(y_train, train_pred)

        test_pred = self.model.predict(X_test_scaled)
        test_accuracy = accuracy_score(y_test, test_pred)
        test_f1 = f1_score(y_test, test_pred, average="weighted")

        # ROC-AUC (macro OVR)
        try:
            test_proba = self.model.predict_proba(X_test_scaled)
            n_classes = len(self.label_map)
            if test_proba.shape[1] == n_classes:
                roc_auc = roc_auc_score(
                    y_test, test_proba, multi_class="ovr", average="macro"
                )
            else:
                roc_auc = None
        except Exception:
            roc_auc = None

        print(f"\n=== Training Results ===")
        print(f"Training accuracy : {train_accuracy:.4f}")
        print(f"Test accuracy     : {test_accuracy:.4f}")
        print(f"Test weighted F1  : {test_f1:.4f}")
        if roc_auc:
            print(f"Test ROC-AUC      : {roc_auc:.4f}")

        # Stratified cross-validation
        print("\nPerforming 5-fold stratified cross-validation...")
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=self.random_state)
        cv_scores = cross_val_score(
            self.model, X_train_scaled, y_train, cv=skf, scoring="accuracy"
        )
        print(f"[OK] CV accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

        # Classification report
        print("\n=== Classification Report ===")
        label_names = [k for k, v in sorted(self.label_map.items(), key=lambda x: x[1])]
        print(classification_report(y_test, test_pred, target_names=label_names))

        # Confusion matrix
        print("=== Confusion Matrix ===")
        cm = confusion_matrix(y_test, test_pred)
        print(cm)

        # Feature importance (from underlying RF when ensemble, else direct)
        feature_importance = self.get_feature_importance()
        if feature_importance:
            print("\n=== Top 10 Important Features ===")
            for i, (feature, importance) in enumerate(feature_importance[:10], 1):
                print(f"{i:2d}. {feature:40s} {importance:.4f}")

        # Store metadata
        self.training_metadata = {
            "model_type": self.model_type,
            "n_samples": len(data),
            "n_features": len(features.columns),
            "train_accuracy": float(train_accuracy),
            "test_accuracy": float(test_accuracy),
            "test_f1": float(test_f1),
            "roc_auc": float(roc_auc) if roc_auc else None,
            "cv_mean": float(cv_scores.mean()),
            "cv_std": float(cv_scores.std()),
            "label_map": self.label_map,
            "feature_names": self.feature_engineer.get_feature_importance_names(),
            "training_date": datetime.now().isoformat(),
            "random_state": self.random_state,
        }

        return {
            "train_accuracy": train_accuracy,
            "test_accuracy": test_accuracy,
            "test_f1": test_f1,
            "roc_auc": roc_auc,
            "cv_scores": cv_scores,
            "confusion_matrix": cm,
            "feature_importance": feature_importance,
        }

    def get_feature_importance(self, top_n: Optional[int] = None) -> list:
        """
        Get feature importance from trained model.
        Works for RandomForest, GradientBoosting, and the calibrated ensemble
        (extracts importances from the underlying RF estimator when available).
        """
        if self.model is None:
            return []

        # Try direct attribute first
        estimator = self.model
        if hasattr(estimator, "calibrated_classifiers_"):
            # CalibratedClassifierCV wraps the base estimator
            try:
                estimator = estimator.calibrated_classifiers_[0].estimator
            except Exception:
                pass

        # VotingClassifier — use RF sub-estimator
        if hasattr(estimator, "estimators_"):
            for name, sub_est in zip(
                [e[0] for e in getattr(estimator, "estimators", [])],
                estimator.estimators_,
            ):
                if hasattr(sub_est, "feature_importances_"):
                    importances = sub_est.feature_importances_
                    break
            else:
                return []
        elif hasattr(estimator, "feature_importances_"):
            importances = estimator.feature_importances_
        else:
            return []

        feature_names = self.feature_engineer.get_feature_importance_names()
        importance_pairs = sorted(
            zip(feature_names, importances),
            key=lambda x: x[1],
            reverse=True,
        )
        return importance_pairs[:top_n] if top_n else importance_pairs

    def save_model(self, output_dir: str = "ml/saved_models"):
        """Save trained classifier, anomaly detector, feature engineer, and metadata."""
        if self.model is None:
            raise ValueError("No model to save")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save classifier
        model_path = output_path / f"model_{timestamp}.joblib"
        joblib.dump(self.model, model_path)
        print(f"\n[OK] Classifier saved to {model_path}")

        # Save anomaly detector
        if self.anomaly_detector:
            anomaly_path = output_path / f"anomaly_{timestamp}.joblib"
            joblib.dump(self.anomaly_detector, anomaly_path)
            anomaly_latest = output_path / "anomaly_latest.joblib"
            joblib.dump(self.anomaly_detector, anomaly_latest)
            print(f"[OK] Anomaly detector saved to {anomaly_path}")

        # Save feature engineer
        fe_path = output_path / f"feature_engineer_{timestamp}.joblib"
        self.feature_engineer.save(fe_path)

        # Save metadata
        metadata_path = output_path / f"metadata_{timestamp}.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(self.training_metadata, f, indent=2)
        print(f"[OK] Metadata saved to {metadata_path}")

        # Save latest
        joblib.dump(self.model, output_path / "model_latest.joblib")
        self.feature_engineer.save(output_path / "feature_engineer_latest.joblib")
        with open(output_path / "metadata_latest.json", "w", encoding="utf-8") as f:
            json.dump(self.training_metadata, f, indent=2)

        print("[OK] Latest versions updated")

        return {
            "model_path": str(model_path),
            "feature_engineer_path": str(fe_path),
            "metadata_path": str(metadata_path),
        }


def main():
    """Main training script"""
    print("=" * 70)
    print("AI PACKAGING RELIABILITY COPILOT - MODEL TRAINING")
    print("Ensemble: RandomForest + GradientBoosting (Calibrated Voting)")
    print("=" * 70)

    # Initialize trainer with ensemble
    trainer = ModelTrainer(model_type="ensemble", random_state=42)

    # Generate 20k training samples for best accuracy
    data = trainer.generate_training_data(n_samples=20000, include_scenarios=True)

    # Train model
    results = trainer.train(data, test_size=0.2)
    
    # Save model
    paths = trainer.save_model()
    
    print("\n" + "=" * 70)
    print("TRAINING COMPLETE")
    print("=" * 70)
    print(f"\nModel files saved:")
    for key, path in paths.items():
        print(f"  {key}: {path}")
    
    print("\n✓ Model ready for deployment")


if __name__ == "__main__":
    main()

# Made with Bob
