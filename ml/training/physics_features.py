"""
Physics-Based Feature Engineering for Packaging Reliability
Implements real semiconductor physics calculations:
- Thermal stress (CTE mismatch)
- Warpage index
- Cure shrinkage stress
- Intermetallic growth
- Moisture-induced stress
Based on Micron Research Report
"""

import numpy as np
from typing import Dict, List
import pandas as pd


class PhysicsFeatureCalculator:
    """
    Calculate physics-based features from process data
    """
    
    # Material properties (typical values for semiconductor packaging)
    MATERIAL_PROPERTIES = {
        'silicon': {
            'CTE': 2.6e-6,  # Coefficient of Thermal Expansion (1/K)
            'youngs_modulus': 130e9,  # Pa
            'poisson_ratio': 0.28,
            'thermal_conductivity': 150,  # W/m·K
        },
        'epoxy_mold': {
            'CTE': 15e-6,  # Below Tg
            'CTE_above_tg': 60e-6,  # Above Tg
            'youngs_modulus': 20e9,  # Pa
            'poisson_ratio': 0.35,
            'Tg': 175,  # Glass transition temperature (°C)
        },
        'copper': {
            'CTE': 17e-6,
            'youngs_modulus': 120e9,
            'poisson_ratio': 0.34,
        },
        'gold_wire': {
            'CTE': 14.2e-6,
            'youngs_modulus': 78e9,
            'yield_strength': 200e6,  # Pa
        },
        'aluminum_wire': {
            'CTE': 23.1e-6,
            'youngs_modulus': 70e9,
            'yield_strength': 100e6,  # Pa
        }
    }
    
    def __init__(self):
        """Initialize physics calculator"""
        self.reference_temp = 25.0  # Reference temperature (°C)
    
    def calculate_thermal_stress(self, data: Dict) -> Dict[str, float]:
        """
        Calculate thermal stress from CTE mismatch
        
        Stress = E * α * ΔT / (1 - ν)
        where:
        E = Young's modulus
        α = CTE difference
        ΔT = Temperature change
        ν = Poisson's ratio
        """
        features = {}
        
        # Die attach thermal stress (Si vs Epoxy)
        die_temp = data.get('die_attach_temperature', 185)
        delta_T = die_temp - self.reference_temp
        
        alpha_diff = abs(
            self.MATERIAL_PROPERTIES['epoxy_mold']['CTE'] - 
            self.MATERIAL_PROPERTIES['silicon']['CTE']
        )
        
        E_eff = (
            self.MATERIAL_PROPERTIES['silicon']['youngs_modulus'] * 
            self.MATERIAL_PROPERTIES['epoxy_mold']['youngs_modulus']
        ) / (
            self.MATERIAL_PROPERTIES['silicon']['youngs_modulus'] + 
            self.MATERIAL_PROPERTIES['epoxy_mold']['youngs_modulus']
        )
        
        thermal_stress = E_eff * alpha_diff * delta_T / (1 - 0.3)
        features['die_attach_thermal_stress'] = thermal_stress / 1e6  # Convert to MPa
        
        # Molding thermal stress
        mold_temp = data.get('mold_temperature', 175)
        mold_delta_T = mold_temp - self.reference_temp
        
        # Check if above Tg (CTE changes dramatically)
        if mold_temp > self.MATERIAL_PROPERTIES['epoxy_mold']['Tg']:
            alpha_mold = self.MATERIAL_PROPERTIES['epoxy_mold']['CTE_above_tg']
        else:
            alpha_mold = self.MATERIAL_PROPERTIES['epoxy_mold']['CTE']
        
        alpha_diff_mold = abs(alpha_mold - self.MATERIAL_PROPERTIES['silicon']['CTE'])
        mold_stress = E_eff * alpha_diff_mold * mold_delta_T / (1 - 0.3)
        features['mold_thermal_stress'] = mold_stress / 1e6  # MPa
        
        # Cumulative thermal budget (integral of temperature over time)
        cure_temp = data.get('cure_temperature', 180)
        cure_time = data.get('cure_time', 150)  # minutes
        features['thermal_budget'] = cure_temp * cure_time  # °C·min
        
        # Temperature cycling stress (max - min temperatures)
        temps = [
            data.get('die_attach_temperature', 185),
            data.get('bonding_temperature', 165),
            data.get('mold_temperature', 175),
            data.get('cure_temperature', 180)
        ]
        features['temperature_range'] = max(temps) - min(temps)
        features['max_process_temp'] = max(temps)
        
        return features
    
    def calculate_warpage_index(self, data: Dict) -> Dict[str, float]:
        """
        Calculate warpage risk index
        
        Warpage ∝ (CTE_mismatch * ΔT * thickness²) / stiffness
        """
        features = {}
        
        # Simplified warpage model
        cure_temp = data.get('cure_temperature', 180)
        delta_T = cure_temp - self.reference_temp
        
        # Assume package thickness ~1mm, die thickness ~0.3mm
        package_thickness = 1.0  # mm
        
        # CTE mismatch between layers
        cte_mismatch = abs(
            self.MATERIAL_PROPERTIES['epoxy_mold']['CTE'] - 
            self.MATERIAL_PROPERTIES['silicon']['CTE']
        )
        
        # Warpage index (dimensionless)
        warpage_index = (cte_mismatch * delta_T * package_thickness**2) * 1e6
        features['warpage_index'] = warpage_index
        
        # Cure shrinkage contribution
        cure_shrinkage = data.get('cure_shrinkage', 1.0)  # %
        features['shrinkage_stress_index'] = cure_shrinkage * delta_T
        
        # Thermal uniformity affects warpage
        thermal_uniformity = data.get('thermal_uniformity', 1.5)
        features['uniformity_warpage_factor'] = thermal_uniformity * warpage_index
        
        return features
    
    def calculate_intermetallic_growth(self, data: Dict) -> Dict[str, float]:
        """
        Calculate intermetallic compound (IMC) growth at wire bonds
        
        IMC thickness ∝ sqrt(D * t) * exp(-Ea/RT)
        where D = diffusion coefficient, t = time, Ea = activation energy
        """
        features = {}
        
        # Simplified Arrhenius model
        bond_temp = data.get('bonding_temperature', 165)  # °C
        bond_time = data.get('bond_time', 20)  # ms
        
        # Convert to Kelvin
        T_kelvin = bond_temp + 273.15
        
        # Activation energy for Au-Al IMC (typical: 1.0 eV)
        Ea = 1.0 * 1.602e-19  # J
        k_B = 1.381e-23  # Boltzmann constant
        
        # Growth rate factor
        growth_factor = np.exp(-Ea / (k_B * T_kelvin))
        
        # IMC thickness index (arbitrary units)
        imc_index = growth_factor * np.sqrt(bond_time)
        features['intermetallic_growth_index'] = imc_index * 1e10  # Scale for readability
        
        # Ultrasonic power affects IMC formation
        ultrasonic = data.get('ultrasonic_power', 90)
        features['ultrasonic_imc_factor'] = ultrasonic * growth_factor * 1e10
        
        return features
    
    def calculate_moisture_stress(self, data: Dict) -> Dict[str, float]:
        """
        Calculate moisture-induced stress (popcorn effect)
        
        Vapor pressure ∝ exp(moisture_content) * exp(-Hv/RT)
        """
        features = {}
        
        # Humidity during cure
        humidity = data.get('cure_humidity', 40)  # %RH
        
        # Reflow temperature (worst case for popcorn)
        reflow_temp = 260  # °C (typical lead-free solder reflow)
        T_kelvin = reflow_temp + 273.15
        
        # Heat of vaporization for water
        Hv = 40.66e3  # J/mol
        R = 8.314  # J/(mol·K)
        
        # Vapor pressure index
        vapor_pressure_index = (humidity / 100) * np.exp(-Hv / (R * T_kelvin))
        features['moisture_vapor_pressure_index'] = vapor_pressure_index * 1e6
        
        # Void percentage amplifies moisture risk
        voids = data.get('die_void_percentage', 1.0) + data.get('mold_voids', 0.5)
        features['moisture_void_risk'] = vapor_pressure_index * voids * 1e6
        
        return features
    
    def calculate_mechanical_stress(self, data: Dict) -> Dict[str, float]:
        """
        Calculate mechanical stress indices
        """
        features = {}
        
        # Wire bond stress from force
        bond_force = data.get('wire_bonding_force', 45)  # gf
        wire_diameter = data.get('wire_diameter', 25)  # μm
        
        # Convert to stress (assuming circular cross-section)
        wire_area = np.pi * (wire_diameter * 1e-6 / 2)**2  # m²
        bond_stress = (bond_force * 9.81e-3) / wire_area  # Pa
        features['wire_bond_stress'] = bond_stress / 1e6  # MPa
        
        # Mold pressure stress
        mold_pressure = data.get('mold_pressure', 7.0)  # MPa
        features['mold_pressure_stress'] = mold_pressure
        
        # Die attach force stress
        die_force = data.get('die_attach_force', 10)  # N
        die_area = 25e-6  # Assume 5mm x 5mm die
        die_stress = die_force / die_area  # Pa
        features['die_attach_stress'] = die_stress / 1e6  # MPa
        
        # Clamp force
        clamp_force = data.get('clamp_force', 60)  # kN
        features['clamp_stress_index'] = clamp_force / 1000  # Normalized
        
        return features
    
    def calculate_process_interactions(self, data: Dict) -> Dict[str, float]:
        """
        Calculate interaction features between process stages
        """
        features = {}
        
        # Die attach quality affects wire bonding
        die_placement = data.get('die_placement_accuracy', 5)  # μm
        wire_loop = data.get('wire_loop_height', 225)  # μm
        features['die_wire_interaction'] = die_placement * wire_loop / 1000
        
        # Void accumulation across stages
        die_voids = data.get('die_void_percentage', 1.0)
        mold_voids = data.get('mold_voids', 0.5)
        features['total_void_index'] = die_voids + mold_voids
        
        # Temperature gradient effects
        temp_range = features.get('temperature_range', 20)
        cure_uniformity = data.get('thermal_uniformity', 1.5)
        features['thermal_gradient_index'] = temp_range * cure_uniformity
        
        # Process time efficiency
        fill_time = data.get('fill_time', 4)  # s
        cure_time = data.get('cure_time', 150)  # min
        features['process_time_ratio'] = cure_time / (fill_time * 60)
        
        # Quality composite score
        visual_score = data.get('visual_score', 95)
        reliability = data.get('reliability_score', 97)
        defects = data.get('defect_count', 0)
        features['quality_composite'] = (visual_score + reliability) / 2 - defects * 5
        
        return features
    
    def calculate_all_physics_features(self, data: Dict) -> Dict[str, float]:
        """
        Calculate all physics-based features
        
        Args:
            data: Process data dictionary
            
        Returns:
            Dictionary of physics-based features
        """
        all_features = {}
        
        # Thermal stress features
        all_features.update(self.calculate_thermal_stress(data))
        
        # Warpage features
        all_features.update(self.calculate_warpage_index(data))
        
        # Intermetallic growth
        all_features.update(self.calculate_intermetallic_growth(data))
        
        # Moisture stress
        all_features.update(self.calculate_moisture_stress(data))
        
        # Mechanical stress
        all_features.update(self.calculate_mechanical_stress(data))
        
        # Process interactions
        all_features.update(self.calculate_process_interactions(data))
        
        return all_features
    
    def calculate_batch_features(self, data_list: List[Dict]) -> pd.DataFrame:
        """
        Calculate physics features for a batch of data
        
        Args:
            data_list: List of process data dictionaries
            
        Returns:
            DataFrame with physics features
        """
        features_list = []
        
        for data in data_list:
            features = self.calculate_all_physics_features(data)
            features_list.append(features)
        
        return pd.DataFrame(features_list)


# Example usage and testing
if __name__ == "__main__":
    print("=== Physics-Based Feature Calculator Test ===\n")
    
    # Test data
    test_data = {
        'die_attach_temperature': 185.0,
        'die_attach_force': 10.0,
        'die_void_percentage': 2.0,
        'die_placement_accuracy': 8.0,
        'bonding_temperature': 165.0,
        'wire_bonding_force': 45.0,
        'ultrasonic_power': 90.0,
        'wire_loop_height': 225.0,
        'wire_diameter': 25.0,
        'bond_time': 20.0,
        'mold_temperature': 175.0,
        'mold_pressure': 7.0,
        'mold_voids': 0.5,
        'fill_time': 4.0,
        'clamp_force': 60.0,
        'cure_temperature': 180.0,
        'cure_time': 150.0,
        'cure_humidity': 40.0,
        'thermal_uniformity': 1.5,
        'cure_shrinkage': 1.0,
        'visual_score': 95.0,
        'reliability_score': 97.0,
        'defect_count': 0,
    }
    
    calculator = PhysicsFeatureCalculator()
    
    # Calculate all features
    features = calculator.calculate_all_physics_features(test_data)
    
    print("Calculated Physics Features:")
    print("-" * 60)
    for feature_name, value in sorted(features.items()):
        print(f"{feature_name:40s}: {value:12.4f}")
    
    print("\n" + "=" * 60)
    print("Key Physics Insights:")
    print("=" * 60)
    print(f"Thermal Stress (Die Attach): {features['die_attach_thermal_stress']:.2f} MPa")
    print(f"Warpage Index: {features['warpage_index']:.4f}")
    print(f"Total Void Risk: {features['total_void_index']:.2f}%")
    print(f"Quality Composite: {features['quality_composite']:.1f}")
    
    print("\n[OK] Physics feature calculator test complete")

# Made with Bob
