"""
Feature engineering for AI Packaging Reliability Copilot ML Model
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from sklearn.preprocessing import StandardScaler
import joblib


class FeatureEngineer:
    """
    Feature engineering for process data classification
    """
    
    def __init__(self):
        """Initialize feature engineer"""
        self.scaler = StandardScaler()
        self.feature_names: List[str] = []
        
    def extract_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Extract and engineer features from raw process data
        
        Args:
            data: Raw process data DataFrame
            
        Returns:
            DataFrame with engineered features
        """
        features = pd.DataFrame()
        
        # ===================================================================
        # RAW FEATURES (33 parameters)
        # ===================================================================
        
        # Die Attach (7 features)
        features['die_temperature'] = data['die_temperature']
        features['die_epoxy_temperature'] = data['die_epoxy_temperature']
        features['die_void_percentage'] = data['die_void_percentage']
        features['die_placement_accuracy'] = data['die_placement_accuracy']
        features['die_bond_line_thickness'] = data['die_bond_line_thickness']
        features['die_cure_time'] = data['die_cure_time']
        features['die_pressure'] = data['die_pressure']
        
        # Wire Bonding (7 features)
        features['wire_bonding_force'] = data['wire_bonding_force']
        features['wire_ultrasonic_power'] = data['wire_ultrasonic_power']
        features['wire_loop_height'] = data['wire_loop_height']
        features['wire_pull_strength'] = data['wire_pull_strength']
        features['wire_bonding_temperature'] = data['wire_bonding_temperature']
        features['wire_diameter'] = data['wire_diameter']
        features['wire_bond_time'] = data['wire_bond_time']
        
        # Molding (7 features)
        features['mold_temperature'] = data['mold_temperature']
        features['mold_pressure'] = data['mold_pressure']
        features['mold_fill_time'] = data['mold_fill_time']
        features['mold_compound_viscosity'] = data['mold_compound_viscosity']
        features['mold_transfer_speed'] = data['mold_transfer_speed']
        features['mold_clamp_force'] = data['mold_clamp_force']
        features['mold_voids'] = data['mold_voids']
        
        # Curing (6 features)
        features['cure_temperature'] = data['cure_temperature']
        features['cure_time'] = data['cure_time']
        features['cure_humidity'] = data['cure_humidity']
        features['cure_thermal_profile'] = data['cure_thermal_profile']
        features['cure_uniformity'] = data['cure_uniformity']
        features['cure_oxygen_level'] = data['cure_oxygen_level']
        
        # Inspection (6 features)
        features['inspect_defect_count'] = data['inspect_defect_count']
        features['inspect_visual_score'] = data['inspect_visual_score']
        features['inspect_electrical_test'] = data['inspect_electrical_test']
        features['inspect_reliability_score'] = data['inspect_reliability_score']
        features['inspect_dimensional_accuracy'] = data['inspect_dimensional_accuracy']
        features['inspect_lead_coplanarity'] = data['inspect_lead_coplanarity']
        
        # ===================================================================
        # ENGINEERED FEATURES
        # ===================================================================
        
        # Temperature Statistics
        temp_cols = ['die_temperature', 'die_epoxy_temperature', 'wire_bonding_temperature',
                     'mold_temperature', 'cure_temperature']
        features['temp_mean'] = data[temp_cols].mean(axis=1)
        features['temp_std'] = data[temp_cols].std(axis=1)
        features['temp_range'] = data[temp_cols].max(axis=1) - data[temp_cols].min(axis=1)
        
        # Pressure Statistics
        pressure_cols = ['die_pressure', 'mold_pressure']
        features['pressure_ratio'] = data['mold_pressure'] / (data['die_pressure'] + 1e-6)
        features['pressure_sum'] = data[pressure_cols].sum(axis=1)
        
        # Time Efficiency
        features['time_efficiency'] = data['cure_time'] / (data['die_cure_time'] + data['wire_bond_time'] + data['mold_fill_time'] + 1e-6)
        
        # Quality Indicators
        features['void_total'] = data['die_void_percentage'] + data['mold_voids']
        features['quality_score'] = (data['inspect_visual_score'] + data['inspect_reliability_score']) / 2
        
        # Cross-Stage Interactions
        features['die_wire_interaction'] = data['die_placement_accuracy'] * data['wire_bonding_force']
        features['wire_mold_interaction'] = data['wire_loop_height'] * data['mold_temperature']
        features['mold_cure_interaction'] = data['mold_voids'] * data['cure_uniformity']
        
        # Defect Indicators
        features['critical_defects'] = (
            (data['die_void_percentage'] > 5).astype(int) +
            (data['wire_pull_strength'] < 6).astype(int) +
            (data['inspect_electrical_test'] == 0).astype(int) +
            (data['inspect_reliability_score'] < 85).astype(int) +
            (data['mold_voids'] > 2).astype(int)
        )
        
        # Thermal Consistency
        features['thermal_consistency'] = 1 / (features['temp_std'] + 1e-6)
        
        # Process Stability (coefficient of variation)
        features['process_stability'] = features['temp_std'] / (features['temp_mean'] + 1e-6)
        
        # Store feature names
        self.feature_names = features.columns.tolist()
        
        return features
    
    def add_rolling_features(
        self,
        data: pd.DataFrame,
        window: int = 5
    ) -> pd.DataFrame:
        """
        Add rolling window features for time-series data
        
        Args:
            data: Feature DataFrame
            window: Rolling window size
            
        Returns:
            DataFrame with rolling features added
        """
        rolling_features = data.copy()
        
        # Rolling mean for key parameters
        key_params = ['die_temperature', 'wire_bonding_force', 'mold_temperature',
                      'cure_temperature', 'inspect_reliability_score']
        
        for param in key_params:
            if param in data.columns:
                rolling_features[f'{param}_rolling_mean'] = data[param].rolling(window=window, min_periods=1).mean()
                rolling_features[f'{param}_rolling_std'] = data[param].rolling(window=window, min_periods=1).std()
        
        return rolling_features
    
    def fit_scaler(self, features: pd.DataFrame):
        """
        Fit the scaler on training data
        
        Args:
            features: Training features
        """
        self.scaler.fit(features)
    
    def transform(self, features: pd.DataFrame) -> np.ndarray:
        """
        Transform features using fitted scaler
        
        Args:
            features: Features to transform
            
        Returns:
            Scaled features
        """
        return self.scaler.transform(features)
    
    def fit_transform(self, features: pd.DataFrame) -> np.ndarray:
        """
        Fit scaler and transform features
        
        Args:
            features: Features to fit and transform
            
        Returns:
            Scaled features
        """
        return self.scaler.fit_transform(features)
    
    def get_feature_importance_names(self) -> List[str]:
        """Get feature names for importance analysis"""
        return self.feature_names
    
    def save(self, filepath: str):
        """
        Save feature engineer (scaler and feature names)
        
        Args:
            filepath: Path to save file
        """
        joblib.dump({
            'scaler': self.scaler,
            'feature_names': self.feature_names
        }, filepath)
        print(f"✓ Feature engineer saved to {filepath}")
    
    def load(self, filepath: str):
        """
        Load feature engineer
        
        Args:
            filepath: Path to load file
        """
        data = joblib.load(filepath)
        self.scaler = data['scaler']
        self.feature_names = data['feature_names']
        print(f"✓ Feature engineer loaded from {filepath}")


def prepare_labels(data: pd.DataFrame) -> Tuple[np.ndarray, Dict[str, int]]:
    """
    Prepare labels for classification
    
    Args:
        data: DataFrame with 'status' column
        
    Returns:
        Tuple of (encoded labels, label mapping)
    """
    # Label mapping
    label_map = {
        'GOOD': 0,
        'WARNING': 1,
        'SEVERE': 2
    }
    
    # Encode labels
    labels = data['status'].map(label_map).values
    
    return labels, label_map


def get_feature_statistics(features: pd.DataFrame) -> pd.DataFrame:
    """
    Get statistics about features
    
    Args:
        features: Feature DataFrame
        
    Returns:
        Statistics DataFrame
    """
    stats = pd.DataFrame({
        'mean': features.mean(),
        'std': features.std(),
        'min': features.min(),
        'max': features.max(),
        'missing': features.isnull().sum()
    })
    
    return stats


if __name__ == "__main__":
    print("=== Feature Engineering Test ===\n")
    
    # Create sample data
    sample_data = pd.DataFrame({
        'die_temperature': [185.0, 187.0, 190.0],
        'die_epoxy_temperature': [155.0, 156.0, 158.0],
        'die_void_percentage': [2.0, 3.5, 6.0],
        'die_placement_accuracy': [8.0, 10.0, 12.0],
        'die_bond_line_thickness': [25.0, 26.0, 27.0],
        'die_cure_time': [75.0, 80.0, 85.0],
        'die_pressure': [0.8, 0.9, 1.0],
        'wire_bonding_force': [45.0, 47.0, 35.0],
        'wire_ultrasonic_power': [90.0, 92.0, 70.0],
        'wire_loop_height': [225.0, 230.0, 190.0],
        'wire_pull_strength': [10.0, 9.0, 5.0],
        'wire_bonding_temperature': [165.0, 167.0, 170.0],
        'wire_diameter': [25.0, 25.0, 25.0],
        'wire_bond_time': [20.0, 21.0, 22.0],
        'mold_temperature': [175.0, 176.0, 178.0],
        'mold_pressure': [7.0, 7.2, 7.5],
        'mold_fill_time': [4.0, 4.2, 4.5],
        'mold_compound_viscosity': [125.0, 130.0, 135.0],
        'mold_transfer_speed': [12.5, 13.0, 13.5],
        'mold_clamp_force': [60.0, 62.0, 65.0],
        'mold_voids': [0.5, 1.0, 2.5],
        'cure_temperature': [180.0, 181.0, 183.0],
        'cure_time': [150.0, 155.0, 160.0],
        'cure_humidity': [40.0, 42.0, 45.0],
        'cure_thermal_profile': [3.0, 3.2, 3.5],
        'cure_uniformity': [1.5, 1.8, 2.5],
        'cure_oxygen_level': [0.5, 0.7, 1.0],
        'inspect_defect_count': [0, 1, 3],
        'inspect_visual_score': [95.0, 88.0, 75.0],
        'inspect_electrical_test': [1, 1, 0],
        'inspect_reliability_score': [97.0, 90.0, 80.0],
        'inspect_dimensional_accuracy': [15.0, 25.0, 45.0],
        'inspect_lead_coplanarity': [40.0, 60.0, 110.0],
        'status': ['GOOD', 'WARNING', 'SEVERE']
    })
    
    # Initialize feature engineer
    fe = FeatureEngineer()
    
    # Extract features
    features = fe.extract_features(sample_data)
    print(f"✓ Extracted {len(features.columns)} features")
    print(f"  Raw features: 33")
    print(f"  Engineered features: {len(features.columns) - 33}")
    
    # Show some engineered features
    print(f"\n✓ Sample engineered features:")
    print(f"  temp_mean: {features['temp_mean'].values}")
    print(f"  void_total: {features['void_total'].values}")
    print(f"  critical_defects: {features['critical_defects'].values}")
    
    # Prepare labels
    labels, label_map = prepare_labels(sample_data)
    print(f"\n✓ Labels prepared: {labels}")
    print(f"  Label mapping: {label_map}")
    
    # Get statistics
    stats = get_feature_statistics(features)
    print(f"\n✓ Feature statistics computed")
    print(f"  Features with missing values: {(stats['missing'] > 0).sum()}")
    
    print("\n=== Test Complete ===")

# Made with Bob
