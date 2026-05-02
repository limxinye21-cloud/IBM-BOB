"""
ML Service for AI Packaging Reliability Copilot
Integrates ML model with backend API
"""

import sys
import os
from typing import Dict, List, Optional
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from ml.training.inference import ModelInference


class MLService:
    """
    Service layer for ML model integration
    """
    
    def __init__(self, model_dir: str = "ml/saved_models"):
        """
        Initialize ML service
        
        Args:
            model_dir: Directory containing saved models
        """
        self.model_dir = model_dir
        self.inference = None
        self._is_loaded = False
        
    def load_model(self, version: str = "latest") -> bool:
        """
        Load ML model
        
        Args:
            version: Model version to load
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.inference = ModelInference(model_dir=self.model_dir)
            self.inference.load_model(version=version)
            self._is_loaded = True
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            self._is_loaded = False
            return False
    
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self._is_loaded
    
    def predict_status(self, process_data: Dict) -> Dict:
        """
        Predict process status
        
        Args:
            process_data: Process parameters
            
        Returns:
            Prediction result with status and confidence
        """
        if not self._is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            result = self.inference.predict_single(process_data)
            return {
                'status': result['status'],
                'confidence': result['confidence'],
                'probabilities': result['probabilities'],
                'timestamp': result['prediction_time']
            }
        except Exception as e:
            print(f"Prediction error: {e}")
            # Fallback to rule-based classification
            return self._rule_based_classification(process_data)
    
    def predict_batch(self, process_data_list: List[Dict]) -> List[Dict]:
        """
        Predict status for multiple data points
        
        Args:
            process_data_list: List of process parameters
            
        Returns:
            List of prediction results
        """
        if not self._is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            results = self.inference.predict_batch(process_data_list)
            return results
        except Exception as e:
            print(f"Batch prediction error: {e}")
            # Fallback to rule-based for each
            return [self._rule_based_classification(data) for data in process_data_list]
    
    def explain_prediction(self, process_data: Dict, top_n: int = 10) -> Dict:
        """
        Explain prediction with feature contributions
        
        Args:
            process_data: Process parameters
            top_n: Number of top features to return
            
        Returns:
            Explanation with top contributing features
        """
        if not self._is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            explanation = self.inference.explain_prediction(process_data, top_n=top_n)
            return explanation
        except Exception as e:
            print(f"Explanation error: {e}")
            return {
                'prediction': self._rule_based_classification(process_data),
                'top_contributors': [],
                'explanation_time': datetime.now().isoformat()
            }
    
    def get_critical_parameters(
        self,
        process_data: Dict,
        threshold: float = 0.05
    ) -> List[Dict]:
        """
        Get critical parameters that need attention
        
        Args:
            process_data: Process parameters
            threshold: Importance threshold
            
        Returns:
            List of critical parameters
        """
        if not self._is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            critical = self.inference.get_critical_parameters(process_data, threshold=threshold)
            return critical
        except Exception as e:
            print(f"Critical parameters error: {e}")
            return []
    
    def get_model_info(self) -> Dict:
        """
        Get model information
        
        Returns:
            Model metadata
        """
        if not self._is_loaded:
            return {
                'status': 'not_loaded',
                'message': 'Model not loaded'
            }
        
        try:
            info = self.inference.get_model_info()
            info['status'] = 'loaded'
            return info
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _rule_based_classification(self, process_data: Dict) -> Dict:
        """
        Fallback rule-based classification when ML model is unavailable
        
        Args:
            process_data: Process parameters
            
        Returns:
            Classification result
        """
        # Count severe conditions
        severe_count = 0
        warning_count = 0
        
        # Die attach checks
        if process_data.get('die_void_percentage', 0) > 5:
            severe_count += 1
        elif process_data.get('die_void_percentage', 0) > 3:
            warning_count += 1
        
        if process_data.get('die_temperature', 185) > 195 or process_data.get('die_temperature', 185) < 175:
            warning_count += 1
        
        # Wire bonding checks
        if process_data.get('wire_pull_strength', 10) < 6:
            severe_count += 1
        elif process_data.get('wire_pull_strength', 10) < 8:
            warning_count += 1
        
        if process_data.get('wire_bonding_force', 45) < 35 or process_data.get('wire_bonding_force', 45) > 55:
            warning_count += 1
        
        # Molding checks
        if process_data.get('mold_voids', 0.5) > 2:
            severe_count += 1
        elif process_data.get('mold_voids', 0.5) > 1:
            warning_count += 1
        
        # Curing checks
        if process_data.get('cure_uniformity', 1.5) > 2.5:
            warning_count += 1
        
        # Inspection checks
        if process_data.get('inspect_electrical_test', 1) == 0:
            severe_count += 1
        
        if process_data.get('inspect_reliability_score', 95) < 85:
            severe_count += 1
        elif process_data.get('inspect_reliability_score', 95) < 90:
            warning_count += 1
        
        if process_data.get('inspect_defect_count', 0) > 2:
            severe_count += 1
        elif process_data.get('inspect_defect_count', 0) > 0:
            warning_count += 1
        
        # Determine status
        if severe_count > 0:
            status = 'SEVERE'
            confidence = 0.7 + (severe_count * 0.05)
        elif warning_count > 1:
            status = 'WARNING'
            confidence = 0.6 + (warning_count * 0.05)
        else:
            status = 'GOOD'
            confidence = 0.8
        
        confidence = min(confidence, 0.95)
        
        return {
            'status': status,
            'confidence': confidence,
            'probabilities': {
                'GOOD': 0.8 if status == 'GOOD' else 0.1,
                'WARNING': 0.7 if status == 'WARNING' else 0.2,
                'SEVERE': 0.8 if status == 'SEVERE' else 0.1
            },
            'timestamp': datetime.now().isoformat(),
            'method': 'rule_based'
        }


# Global ML service instance
_ml_service: Optional[MLService] = None


def get_ml_service() -> MLService:
    """
    Get or create ML service singleton
    
    Returns:
        ML service instance
    """
    global _ml_service
    if _ml_service is None:
        _ml_service = MLService()
        # Try to load model
        _ml_service.load_model()
    return _ml_service


def initialize_ml_service(model_dir: str = "ml/saved_models") -> bool:
    """
    Initialize ML service with specific model directory
    
    Args:
        model_dir: Directory containing saved models
        
    Returns:
        True if successful
    """
    global _ml_service
    _ml_service = MLService(model_dir=model_dir)
    return _ml_service.load_model()


if __name__ == "__main__":
    print("=== ML Service Test ===\n")
    
    # Test data
    test_data = {
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
    
    # Initialize service
    service = get_ml_service()
    
    if service.is_loaded():
        print("✓ ML model loaded successfully\n")
        
        # Get model info
        info = service.get_model_info()
        print("Model Info:")
        print(f"  Type: {info.get('model_type')}")
        print(f"  Accuracy: {info.get('test_accuracy', 0):.4f}")
        
        # Predict
        print("\nPrediction:")
        result = service.predict_status(test_data)
        print(f"  Status: {result['status']}")
        print(f"  Confidence: {result['confidence']:.4f}")
        
    else:
        print("⚠ ML model not available, using rule-based classification\n")
        
        # Test rule-based
        result = service._rule_based_classification(test_data)
        print("Rule-based Classification:")
        print(f"  Status: {result['status']}")
        print(f"  Confidence: {result['confidence']:.4f}")
    
    print("\n✓ ML Service test complete")

# Made with Bob
