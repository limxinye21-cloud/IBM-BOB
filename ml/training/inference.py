"""
Inference pipeline for AI Packaging Reliability Copilot ML Model
"""

import numpy as np
import pandas as pd
import joblib
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class ModelInference:
    """
    Inference pipeline for real-time process classification
    """
    
    def __init__(self, model_dir: str = "ml/saved_models"):
        """
        Initialize inference pipeline
        
        Args:
            model_dir: Directory containing saved models
        """
        self.model_dir = Path(model_dir)
        self.model = None
        self.feature_engineer = None
        self.metadata = None
        self.label_map = None
        self.reverse_label_map = None
        
    def load_model(self, version: str = "latest"):
        """
        Load trained model and feature engineer
        
        Args:
            version: Model version to load ("latest" or timestamp)
        """
        print(f"\n=== Loading Model ===")
        print(f"Model directory: {self.model_dir}")
        print(f"Version: {version}")
        
        if version == "latest":
            model_path = self.model_dir / "model_latest.joblib"
            fe_path = self.model_dir / "feature_engineer_latest.joblib"
            metadata_path = self.model_dir / "metadata_latest.json"
        else:
            model_path = self.model_dir / f"model_{version}.joblib"
            fe_path = self.model_dir / f"feature_engineer_{version}.joblib"
            metadata_path = self.model_dir / f"metadata_{version}.json"
        
        # Check if files exist
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")
        if not fe_path.exists():
            raise FileNotFoundError(f"Feature engineer not found: {fe_path}")
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata not found: {metadata_path}")
        
        # Load model
        self.model = joblib.load(model_path)
        print(f"[OK] Model loaded from {model_path}")
        
        # Load feature engineer
        fe_data = joblib.load(fe_path)
        from ml.training.features import FeatureEngineer
        self.feature_engineer = FeatureEngineer()
        self.feature_engineer.scaler = fe_data['scaler']
        self.feature_engineer.feature_names = fe_data['feature_names']
        print(f"[OK] Feature engineer loaded from {fe_path}")
        
        # Load metadata
        with open(metadata_path, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)
        print(f"[OK] Metadata loaded from {metadata_path}")
        
        # Create label maps
        self.label_map = self.metadata['label_map']
        self.reverse_label_map = {v: k for k, v in self.label_map.items()}
        
        print(f"\n[OK] Model ready for inference")
        print(f"  Model type: {self.metadata['model_type']}")
        print(f"  Training accuracy: {self.metadata['train_accuracy']:.4f}")
        print(f"  Test accuracy: {self.metadata['test_accuracy']:.4f}")
        print(f"  Features: {self.metadata['n_features']}")
        print(f"  Classes: {list(self.label_map.keys())}")
    
    def predict_single(self, data: Dict) -> Dict:
        """
        Predict status for a single data point
        
        Args:
            data: Process data dictionary
            
        Returns:
            Prediction result dictionary
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        # Convert to DataFrame
        df = pd.DataFrame([data])
        
        # Extract features
        features = self.feature_engineer.extract_features(df)
        
        # Scale features
        features_scaled = self.feature_engineer.transform(features)
        
        # Predict
        prediction = self.model.predict(features_scaled)[0]
        probabilities = self.model.predict_proba(features_scaled)[0]
        
        # Get status label
        status = self.reverse_label_map[prediction]
        
        # Create probability dictionary
        prob_dict = {
            self.reverse_label_map[i]: float(prob)
            for i, prob in enumerate(probabilities)
        }
        
        # Get feature importance for this prediction
        feature_values = features.iloc[0].to_dict()
        
        return {
            'status': status,
            'confidence': float(probabilities[prediction]),
            'probabilities': prob_dict,
            'prediction_time': datetime.now().isoformat(),
            'feature_values': feature_values
        }
    
    def predict_batch(self, data: List[Dict]) -> List[Dict]:
        """
        Predict status for multiple data points
        
        Args:
            data: List of process data dictionaries
            
        Returns:
            List of prediction result dictionaries
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Extract features
        features = self.feature_engineer.extract_features(df)
        
        # Scale features
        features_scaled = self.feature_engineer.transform(features)
        
        # Predict
        predictions = self.model.predict(features_scaled)
        probabilities = self.model.predict_proba(features_scaled)
        
        # Create results
        results = []
        for i, (pred, probs) in enumerate(zip(predictions, probabilities)):
            status = self.reverse_label_map[pred]
            prob_dict = {
                self.reverse_label_map[j]: float(prob)
                for j, prob in enumerate(probs)
            }
            
            results.append({
                'status': status,
                'confidence': float(probs[pred]),
                'probabilities': prob_dict,
                'prediction_time': datetime.now().isoformat()
            })
        
        return results
    
    def explain_prediction(
        self,
        data: Dict,
        top_n: int = 10
    ) -> Dict:
        """
        Explain prediction with feature contributions
        
        Args:
            data: Process data dictionary
            top_n: Number of top contributing features
            
        Returns:
            Explanation dictionary
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        # Get prediction
        prediction_result = self.predict_single(data)
        
        # Get feature importance from model
        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
            feature_names = self.feature_engineer.get_feature_importance_names()
            
            # Get feature values
            df = pd.DataFrame([data])
            features = self.feature_engineer.extract_features(df)
            feature_values = features.iloc[0]
            
            # Calculate contribution (importance * normalized value)
            contributions = []
            for name, importance, value in zip(feature_names, importances, feature_values):
                contributions.append({
                    'feature': name,
                    'value': float(value),
                    'importance': float(importance),
                    'contribution': float(importance * abs(value))
                })
            
            # Sort by contribution
            contributions.sort(key=lambda x: x['contribution'], reverse=True)
            
            # Get top contributors
            top_contributors = contributions[:top_n]
        else:
            top_contributors = []
        
        return {
            'prediction': prediction_result,
            'top_contributors': top_contributors,
            'explanation_time': datetime.now().isoformat()
        }
    
    def get_critical_parameters(
        self,
        data: Dict,
        threshold: float = 0.05
    ) -> List[Dict]:
        """
        Identify critical parameters that need attention
        
        Args:
            data: Process data dictionary
            threshold: Importance threshold
            
        Returns:
            List of critical parameters
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        # Get feature importance
        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
            feature_names = self.feature_engineer.get_feature_importance_names()
            
            # Get feature values
            df = pd.DataFrame([data])
            features = self.feature_engineer.extract_features(df)
            feature_values = features.iloc[0]
            
            # Identify critical parameters
            critical = []
            for name, importance, value in zip(feature_names, importances, feature_values):
                if importance >= threshold:
                    critical.append({
                        'parameter': name,
                        'value': float(value),
                        'importance': float(importance),
                        'is_critical': bool(importance >= threshold * 2)
                    })
            
            # Sort by importance
            critical.sort(key=lambda x: x['importance'], reverse=True)
            
            return critical
        
        return []
    
    def get_model_info(self) -> Dict:
        """
        Get model information
        
        Returns:
            Model information dictionary
        """
        if self.metadata is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        return {
            'model_type': self.metadata['model_type'],
            'training_date': self.metadata['training_date'],
            'n_samples': self.metadata['n_samples'],
            'n_features': self.metadata['n_features'],
            'train_accuracy': self.metadata['train_accuracy'],
            'test_accuracy': self.metadata['test_accuracy'],
            'cv_mean': self.metadata['cv_mean'],
            'cv_std': self.metadata['cv_std'],
            'classes': list(self.label_map.keys())
        }


def test_inference():
    """Test inference pipeline"""
    print("=" * 70)
    print("INFERENCE PIPELINE TEST")
    print("=" * 70)
    
    # Sample data (GOOD condition)
    good_data = {
        'die_temperature': 185.0,
        'die_epoxy_temperature': 155.0,
        'die_void_percentage': 2.0,
        'die_placement_accuracy': 8.0,
        'die_bond_line_thickness': 25.0,
        'die_cure_time': 75.0,
        'die_pressure': 0.8,
        'wire_bonding_force': 45.0,
        'wire_ultrasonic_power': 90.0,
        'wire_loop_height': 225.0,
        'wire_pull_strength': 10.0,
        'wire_bonding_temperature': 165.0,
        'wire_diameter': 25.0,
        'wire_bond_time': 20.0,
        'mold_temperature': 175.0,
        'mold_pressure': 7.0,
        'mold_fill_time': 4.0,
        'mold_compound_viscosity': 125.0,
        'mold_transfer_speed': 12.5,
        'mold_clamp_force': 60.0,
        'mold_voids': 0.5,
        'cure_temperature': 180.0,
        'cure_time': 150.0,
        'cure_humidity': 40.0,
        'cure_thermal_profile': 3.0,
        'cure_uniformity': 1.5,
        'cure_oxygen_level': 0.5,
        'inspect_defect_count': 0,
        'inspect_visual_score': 95.0,
        'inspect_electrical_test': 1,
        'inspect_reliability_score': 97.0,
        'inspect_dimensional_accuracy': 15.0,
        'inspect_lead_coplanarity': 40.0
    }
    
    try:
        # Initialize inference
        inference = ModelInference()
        
        # Load model
        inference.load_model(version="latest")
        
        # Get model info
        print("\n=== Model Information ===")
        info = inference.get_model_info()
        for key, value in info.items():
            print(f"{key}: {value}")
        
        # Predict
        print("\n=== Single Prediction ===")
        result = inference.predict_single(good_data)
        print(f"Status: {result['status']}")
        print(f"Confidence: {result['confidence']:.4f}")
        print(f"Probabilities:")
        for status, prob in result['probabilities'].items():
            print(f"  {status}: {prob:.4f}")
        
        # Explain
        print("\n=== Prediction Explanation ===")
        explanation = inference.explain_prediction(good_data, top_n=5)
        print(f"Top 5 contributing features:")
        for contrib in explanation['top_contributors']:
            print(f"  {contrib['feature']:40s} importance={contrib['importance']:.4f}")
        
        # Critical parameters
        print("\n=== Critical Parameters ===")
        critical = inference.get_critical_parameters(good_data, threshold=0.02)
        print(f"Found {len(critical)} critical parameters")
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
