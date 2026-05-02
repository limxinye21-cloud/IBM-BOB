"""
Training pipeline for AI Packaging Reliability Copilot ML Model
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple, Optional
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from ml.training.features import FeatureEngineer, prepare_labels
from data.mock.generator import MockDataGenerator
from data.mock.scenarios import SCENARIOS


class ModelTrainer:
    """
    Training pipeline for process classification model
    """
    
    def __init__(
        self,
        model_type: str = "random_forest",
        random_state: int = 42
    ):
        """
        Initialize model trainer
        
        Args:
            model_type: Type of model to train
            random_state: Random seed for reproducibility
        """
        self.model_type = model_type
        self.random_state = random_state
        self.model = None
        self.feature_engineer = FeatureEngineer()
        self.label_map = None
        self.training_metadata = {}
        
    def create_model(self) -> RandomForestClassifier:
        """
        Create ML model
        
        Returns:
            Initialized model
        """
        if self.model_type == "random_forest":
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                max_features='sqrt',
                random_state=self.random_state,
                n_jobs=-1,
                class_weight='balanced'  # Handle class imbalance
            )
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
        
        return model
    
    def generate_training_data(
        self,
        n_samples: int = 10000,
        include_scenarios: bool = True
    ) -> pd.DataFrame:
        """
        Generate training data using mock data generator
        
        Args:
            n_samples: Number of samples to generate
            include_scenarios: Whether to include scenario-based data
            
        Returns:
            Training data DataFrame
        """
        print(f"\n=== Generating Training Data ===")
        print(f"Target samples: {n_samples}")
        
        generator = MockDataGenerator()
        all_data = []
        
        # Generate normal operation data (60%)
        normal_samples = int(n_samples * 0.6)
        print(f"Generating {normal_samples} normal samples...")
        for _ in range(normal_samples):
            data = generator.generate_single()
            all_data.append(data)
        
        # Generate scenario-based data (40%)
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
        
        # Print distribution
        status_dist = df['status'].value_counts()
        print(f"\n✓ Generated {len(df)} samples")
        print(f"  Status distribution:")
        for status, count in status_dist.items():
            print(f"    {status}: {count} ({count/len(df)*100:.1f}%)")
        
        return df
    
    def train(
        self,
        data: pd.DataFrame,
        test_size: float = 0.2,
        validation_split: float = 0.1
    ) -> Dict:
        """
        Train the model
        
        Args:
            data: Training data
            test_size: Test set size
            validation_split: Validation set size
            
        Returns:
            Training results dictionary
        """
        print(f"\n=== Training Model ===")
        print(f"Model type: {self.model_type}")
        print(f"Total samples: {len(data)}")
        
        # Extract features
        print("\nExtracting features...")
        features = self.feature_engineer.extract_features(data)
        print(f"✓ Extracted {len(features.columns)} features")
        
        # Prepare labels
        labels, self.label_map = prepare_labels(data)
        print(f"✓ Prepared labels with {len(self.label_map)} classes")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            features, labels,
            test_size=test_size,
            random_state=self.random_state,
            stratify=labels
        )
        
        print(f"\n✓ Data split:")
        print(f"  Training: {len(X_train)} samples")
        print(f"  Testing: {len(X_test)} samples")
        
        # Scale features
        print("\nScaling features...")
        X_train_scaled = self.feature_engineer.fit_transform(X_train)
        X_test_scaled = self.feature_engineer.transform(X_test)
        print("✓ Features scaled")
        
        # Create and train model
        print(f"\nTraining {self.model_type}...")
        self.model = self.create_model()
        self.model.fit(X_train_scaled, y_train)
        print("✓ Model trained")
        
        # Evaluate on training set
        train_pred = self.model.predict(X_train_scaled)
        train_accuracy = accuracy_score(y_train, train_pred)
        
        # Evaluate on test set
        test_pred = self.model.predict(X_test_scaled)
        test_accuracy = accuracy_score(y_test, test_pred)
        
        print(f"\n=== Training Results ===")
        print(f"Training accuracy: {train_accuracy:.4f}")
        print(f"Test accuracy: {test_accuracy:.4f}")
        
        # Cross-validation
        print("\nPerforming cross-validation...")
        cv_scores = cross_val_score(
            self.model, X_train_scaled, y_train,
            cv=5, scoring='accuracy'
        )
        print(f"✓ CV accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        
        # Classification report
        print("\n=== Classification Report ===")
        label_names = [k for k, v in sorted(self.label_map.items(), key=lambda x: x[1])]
        print(classification_report(y_test, test_pred, target_names=label_names))
        
        # Confusion matrix
        print("=== Confusion Matrix ===")
        cm = confusion_matrix(y_test, test_pred)
        print(cm)
        
        # Feature importance
        feature_importance = self.get_feature_importance()
        print("\n=== Top 10 Important Features ===")
        for i, (feature, importance) in enumerate(feature_importance[:10], 1):
            print(f"{i:2d}. {feature:40s} {importance:.4f}")
        
        # Store metadata
        self.training_metadata = {
            'model_type': self.model_type,
            'n_samples': len(data),
            'n_features': len(features.columns),
            'train_accuracy': float(train_accuracy),
            'test_accuracy': float(test_accuracy),
            'cv_mean': float(cv_scores.mean()),
            'cv_std': float(cv_scores.std()),
            'label_map': self.label_map,
            'feature_names': self.feature_engineer.get_feature_importance_names(),
            'training_date': datetime.now().isoformat(),
            'random_state': self.random_state
        }
        
        return {
            'train_accuracy': train_accuracy,
            'test_accuracy': test_accuracy,
            'cv_scores': cv_scores,
            'confusion_matrix': cm,
            'feature_importance': feature_importance
        }
    
    def get_feature_importance(self, top_n: Optional[int] = None) -> list:
        """
        Get feature importance from trained model
        
        Args:
            top_n: Number of top features to return
            
        Returns:
            List of (feature_name, importance) tuples
        """
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
            feature_names = self.feature_engineer.get_feature_importance_names()
            
            # Sort by importance
            importance_pairs = sorted(
                zip(feature_names, importances),
                key=lambda x: x[1],
                reverse=True
            )
            
            if top_n:
                return importance_pairs[:top_n]
            return importance_pairs
        else:
            return []
    
    def save_model(self, output_dir: str = "ml/saved_models"):
        """
        Save trained model and metadata
        
        Args:
            output_dir: Directory to save model
        """
        if self.model is None:
            raise ValueError("No model to save")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save model
        model_path = output_path / f"model_{timestamp}.joblib"
        joblib.dump(self.model, model_path)
        print(f"\n✓ Model saved to {model_path}")
        
        # Save feature engineer
        fe_path = output_path / f"feature_engineer_{timestamp}.joblib"
        self.feature_engineer.save(fe_path)
        
        # Save metadata
        metadata_path = output_path / f"metadata_{timestamp}.json"
        with open(metadata_path, 'w') as f:
            json.dump(self.training_metadata, f, indent=2)
        print(f"✓ Metadata saved to {metadata_path}")
        
        # Save latest symlinks
        latest_model = output_path / "model_latest.joblib"
        latest_fe = output_path / "feature_engineer_latest.joblib"
        latest_metadata = output_path / "metadata_latest.json"
        
        # Copy to latest
        joblib.dump(self.model, latest_model)
        self.feature_engineer.save(latest_fe)
        with open(latest_metadata, 'w') as f:
            json.dump(self.training_metadata, f, indent=2)
        
        print(f"✓ Latest versions updated")
        
        return {
            'model_path': str(model_path),
            'feature_engineer_path': str(fe_path),
            'metadata_path': str(metadata_path)
        }


def main():
    """Main training script"""
    print("=" * 70)
    print("AI PACKAGING RELIABILITY COPILOT - MODEL TRAINING")
    print("=" * 70)
    
    # Initialize trainer
    trainer = ModelTrainer(model_type="random_forest", random_state=42)
    
    # Generate training data
    data = trainer.generate_training_data(n_samples=10000, include_scenarios=True)
    
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
