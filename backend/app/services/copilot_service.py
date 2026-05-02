"""
AI Copilot Service for AI Packaging Reliability Copilot
Intelligent reasoning and natural language interaction powered by IBM Bob
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json

from backend.app.services.ml_service import get_ml_service
from data.mock.config_schema import PARAMETER_RANGES, ISSUE_TO_PARAMETER_MAP, CROSS_STAGE_DEPENDENCIES


class CopilotService:
    """
    AI Copilot service for intelligent manufacturing assistance
    """
    
    def __init__(self):
        """Initialize copilot service"""
        self.ml_service = get_ml_service()
        self.knowledge_base = self._build_knowledge_base()
        
    def _build_knowledge_base(self) -> Dict:
        """
        Build knowledge base from parameter definitions
        
        Returns:
            Knowledge base dictionary
        """
        return {
            'parameters': PARAMETER_RANGES,
            'issue_mapping': ISSUE_TO_PARAMETER_MAP,
            'dependencies': CROSS_STAGE_DEPENDENCIES,
            'stages': {
                'die_attach': {
                    'description': 'Die attachment to substrate using epoxy',
                    'critical_params': ['die_temperature', 'die_void_percentage', 'die_placement_accuracy'],
                    'common_issues': ['voids', 'misalignment', 'temperature instability']
                },
                'wire_bonding': {
                    'description': 'Wire connections between die and package',
                    'critical_params': ['wire_bonding_force', 'wire_pull_strength', 'wire_loop_height'],
                    'common_issues': ['weak bonds', 'wire breaks', 'loop collapse']
                },
                'molding': {
                    'description': 'Encapsulation with molding compound',
                    'critical_params': ['mold_temperature', 'mold_pressure', 'mold_voids'],
                    'common_issues': ['voids', 'incomplete fill', 'wire sweep']
                },
                'curing': {
                    'description': 'Thermal curing of molding compound',
                    'critical_params': ['cure_temperature', 'cure_uniformity', 'cure_time'],
                    'common_issues': ['incomplete cure', 'thermal stress', 'non-uniformity']
                },
                'inspection': {
                    'description': 'Final quality inspection and testing',
                    'critical_params': ['inspect_reliability_score', 'inspect_defect_count', 'inspect_electrical_test'],
                    'common_issues': ['electrical failures', 'visual defects', 'dimensional issues']
                }
            }
        }
    
    def process_query(self, query: str, context: Optional[Dict] = None) -> Dict:
        """
        Process natural language query
        
        Args:
            query: User query
            context: Optional context (current data, predictions, etc.)
            
        Returns:
            Response dictionary with answer and actions
        """
        query_lower = query.lower()
        
        # Determine query type
        if any(word in query_lower for word in ['why', 'reason', 'cause']):
            return self._handle_why_query(query, context)
        
        elif any(word in query_lower for word in ['analyze', 'analysis', 'check']):
            return self._handle_analysis_query(query, context)
        
        elif any(word in query_lower for word in ['recommend', 'suggest', 'optimize', 'improve']):
            return self._handle_recommendation_query(query, context)
        
        elif any(word in query_lower for word in ['what', 'explain', 'tell']):
            return self._handle_explanation_query(query, context)
        
        elif any(word in query_lower for word in ['compare', 'difference']):
            return self._handle_comparison_query(query, context)
        
        else:
            return self._handle_general_query(query, context)
    
    def _handle_why_query(self, query: str, context: Optional[Dict]) -> Dict:
        """Handle 'why' questions about status or issues"""
        
        if not context or 'current_data' not in context:
            return {
                'type': 'why',
                'answer': "I need current process data to analyze the issue. Please provide the data or generate new data first.",
                'confidence': 0.0,
                'actions': ['generate_data']
            }
        
        data = context['current_data']
        status = data.get('predicted_status', data.get('status', 'UNKNOWN'))
        
        # Get prediction explanation
        if self.ml_service.is_loaded():
            explanation = self.ml_service.explain_prediction(data, top_n=5)
            top_features = explanation.get('top_contributors', [])
        else:
            top_features = []
        
        # Identify abnormal parameters
        abnormal_params = self._identify_abnormal_parameters(data)
        
        # Build explanation
        if status == 'SEVERE':
            answer = f"**The batch is classified as SEVERE due to critical issues:**\n\n"
            
            if abnormal_params:
                answer += "**Critical Parameters:**\n"
                for param, info in abnormal_params[:3]:
                    answer += f"- **{param}**: {info['value']:.2f} {info['unit']} "
                    answer += f"(Normal: {info['normal_min']}-{info['normal_max']} {info['unit']})\n"
                    answer += f"  *Impact*: {info['impact']}\n"
            
            if top_features:
                answer += "\n**Top Contributing Factors (ML Analysis):**\n"
                for feat in top_features[:3]:
                    answer += f"- {feat['feature']}: Importance {feat['importance']:.1%}\n"
            
            # Cross-stage analysis
            cross_stage = self._analyze_cross_stage_impact(data, abnormal_params)
            if cross_stage:
                answer += f"\n**Cross-Stage Impact:**\n{cross_stage}"
            
            confidence = 0.9
        
        elif status == 'WARNING':
            answer = f"**The batch is classified as WARNING due to parameters outside normal range:**\n\n"
            
            if abnormal_params:
                answer += "**Parameters Needing Attention:**\n"
                for param, info in abnormal_params[:3]:
                    answer += f"- **{param}**: {info['value']:.2f} {info['unit']} "
                    answer += f"(Warning threshold: {info['warning_threshold']} {info['unit']})\n"
            
            answer += "\n*These parameters should be monitored closely to prevent escalation to SEVERE.*"
            confidence = 0.8
        
        else:  # GOOD
            answer = "**The batch is classified as GOOD:**\n\n"
            answer += "All parameters are within normal operating ranges. "
            answer += "The process is stable and no immediate action is required."
            confidence = 0.95
        
        return {
            'type': 'why',
            'answer': answer,
            'confidence': confidence,
            'abnormal_parameters': abnormal_params,
            'top_features': top_features,
            'actions': ['review_parameters', 'monitor_trends']
        }
    
    def _handle_analysis_query(self, query: str, context: Optional[Dict]) -> Dict:
        """Handle analysis requests"""
        
        query_lower = query.lower()
        
        # Determine what to analyze
        if 'die attach' in query_lower or 'die' in query_lower:
            stage = 'die_attach'
        elif 'wire bond' in query_lower or 'wire' in query_lower or 'bonding' in query_lower:
            stage = 'wire_bonding'
        elif 'mold' in query_lower:
            stage = 'molding'
        elif 'cur' in query_lower:
            stage = 'curing'
        elif 'inspect' in query_lower:
            stage = 'inspection'
        else:
            stage = 'all'
        
        if not context or 'current_data' not in context:
            return {
                'type': 'analysis',
                'answer': f"I can analyze the {stage} stage once you provide process data.",
                'confidence': 0.0,
                'actions': ['generate_data']
            }
        
        data = context['current_data']
        
        if stage == 'all':
            return self._analyze_all_stages(data)
        else:
            return self._analyze_specific_stage(data, stage)
    
    def _handle_recommendation_query(self, query: str, context: Optional[Dict]) -> Dict:
        """Handle recommendation requests"""
        
        if not context or 'current_data' not in context:
            return {
                'type': 'recommendation',
                'answer': "I need current process data to provide recommendations.",
                'confidence': 0.0,
                'actions': ['generate_data']
            }
        
        data = context['current_data']
        status = data.get('predicted_status', data.get('status', 'UNKNOWN'))
        
        # Identify issues
        abnormal_params = self._identify_abnormal_parameters(data)
        
        if not abnormal_params:
            return {
                'type': 'recommendation',
                'answer': "**Process is operating normally. No adjustments needed.**\n\nContinue monitoring for any parameter drift.",
                'confidence': 0.9,
                'actions': ['continue_monitoring']
            }
        
        # Generate recommendations
        recommendations = []
        
        for param, info in abnormal_params[:5]:
            rec = self._generate_parameter_recommendation(param, info)
            if rec:
                recommendations.append(rec)
        
        answer = f"**Optimization Recommendations for {status} Status:**\n\n"
        
        for i, rec in enumerate(recommendations, 1):
            answer += f"**{i}. {rec['parameter']}**\n"
            answer += f"   Current: {rec['current']:.2f} {rec['unit']}\n"
            answer += f"   Target: {rec['target_min']}-{rec['target_max']} {rec['unit']}\n"
            answer += f"   Action: {rec['action']}\n"
            answer += f"   Priority: {rec['priority']}\n\n"
        
        answer += "**Implementation Order:**\n"
        answer += "1. Address CRITICAL priority items first\n"
        answer += "2. Monitor for 5-10 cycles after each adjustment\n"
        answer += "3. Verify improvement before next adjustment\n"
        
        return {
            'type': 'recommendation',
            'answer': answer,
            'confidence': 0.85,
            'recommendations': recommendations,
            'actions': ['implement_recommendations', 'monitor_results']
        }
    
    def _handle_explanation_query(self, query: str, context: Optional[Dict]) -> Dict:
        """Handle explanation requests"""
        
        query_lower = query.lower()
        
        # Check what needs explanation
        for stage_key, stage_info in self.knowledge_base['stages'].items():
            if stage_key.replace('_', ' ') in query_lower:
                answer = f"**{stage_key.replace('_', ' ').title()} Stage:**\n\n"
                answer += f"{stage_info['description']}\n\n"
                answer += f"**Critical Parameters:**\n"
                for param in stage_info['critical_params']:
                    param_info = self.knowledge_base['parameters'].get(param, {})
                    answer += f"- {param}: {param_info.get('normal_min', 0)}-{param_info.get('normal_max', 0)} {param_info.get('unit', '')}\n"
                answer += f"\n**Common Issues:**\n"
                for issue in stage_info['common_issues']:
                    answer += f"- {issue}\n"
                
                return {
                    'type': 'explanation',
                    'answer': answer,
                    'confidence': 1.0,
                    'actions': []
                }
        
        # General explanation
        return {
            'type': 'explanation',
            'answer': "I can explain any aspect of the packaging process. Try asking about specific stages (die attach, wire bonding, molding, curing, inspection) or parameters.",
            'confidence': 0.7,
            'actions': []
        }
    
    def _handle_comparison_query(self, query: str, context: Optional[Dict]) -> Dict:
        """Handle comparison requests"""
        
        return {
            'type': 'comparison',
            'answer': "Comparison feature coming soon. I'll be able to compare batches, parameters, and time periods.",
            'confidence': 0.5,
            'actions': []
        }
    
    def _handle_general_query(self, query: str, context: Optional[Dict]) -> Dict:
        """Handle general queries"""
        
        return {
            'type': 'general',
            'answer': "I'm your AI packaging reliability copilot. I can help you:\n\n" +
                     "- **Analyze** process issues: 'Analyze wire bonding'\n" +
                     "- **Explain** why status is severe: 'Why is this batch severe?'\n" +
                     "- **Recommend** optimizations: 'How can I improve this process?'\n" +
                     "- **Explain** stages: 'Explain die attach stage'\n\n" +
                     "What would you like to know?",
            'confidence': 0.8,
            'actions': []
        }
    
    def _identify_abnormal_parameters(self, data: Dict) -> List[Tuple[str, Dict]]:
        """
        Identify parameters outside normal range
        
        Args:
            data: Process data
            
        Returns:
            List of (parameter_name, info_dict) tuples
        """
        abnormal = []
        
        for param, ranges in self.knowledge_base['parameters'].items():
            if param not in data:
                continue
            
            value = data[param]
            normal_min = ranges.get('normal_min', 0)
            normal_max = ranges.get('normal_max', 100)
            warning_threshold = ranges.get('warning_threshold', normal_max * 0.9)
            severe_threshold = ranges.get('severe_threshold', normal_max * 0.95)
            
            if value < normal_min or value > normal_max:
                severity = 'SEVERE' if (value > severe_threshold or value < normal_min * 0.8) else 'WARNING'
                
                abnormal.append((param, {
                    'value': value,
                    'normal_min': normal_min,
                    'normal_max': normal_max,
                    'warning_threshold': warning_threshold,
                    'severe_threshold': severe_threshold,
                    'unit': ranges.get('unit', ''),
                    'severity': severity,
                    'impact': ranges.get('description', 'Parameter outside normal range')
                }))
        
        # Sort by severity
        abnormal.sort(key=lambda x: (x[1]['severity'] == 'SEVERE', abs(x[1]['value'] - (x[1]['normal_min'] + x[1]['normal_max'])/2)), reverse=True)
        
        return abnormal
    
    def _analyze_cross_stage_impact(self, data: Dict, abnormal_params: List) -> str:
        """Analyze cross-stage dependencies"""
        
        impacts = []
        
        for param, info in abnormal_params[:3]:
            # Check if this parameter affects other stages
            for dep in self.knowledge_base['dependencies']:
                if param in dep.get('source_params', []):
                    impacts.append(f"- {param} issue may affect {dep['target_stage']} stage")
        
        return "\n".join(impacts) if impacts else ""
    
    def _analyze_all_stages(self, data: Dict) -> Dict:
        """Analyze all process stages"""
        
        answer = "**Complete Process Analysis:**\n\n"
        
        for stage_key, stage_info in self.knowledge_base['stages'].items():
            stage_status = self._get_stage_status(data, stage_info['critical_params'])
            answer += f"**{stage_key.replace('_', ' ').title()}**: {stage_status['status']}\n"
            if stage_status['issues']:
                for issue in stage_status['issues']:
                    answer += f"  - {issue}\n"
            answer += "\n"
        
        return {
            'type': 'analysis',
            'answer': answer,
            'confidence': 0.85,
            'actions': ['review_critical_stages']
        }
    
    def _analyze_specific_stage(self, data: Dict, stage: str) -> Dict:
        """Analyze specific process stage"""
        
        stage_info = self.knowledge_base['stages'].get(stage, {})
        
        if not stage_info:
            return {
                'type': 'analysis',
                'answer': f"Unknown stage: {stage}",
                'confidence': 0.0,
                'actions': []
            }
        
        answer = f"**{stage.replace('_', ' ').title()} Stage Analysis:**\n\n"
        answer += f"{stage_info['description']}\n\n"
        
        # Check critical parameters
        answer += "**Parameter Status:**\n"
        for param in stage_info['critical_params']:
            if param in data:
                value = data[param]
                param_info = self.knowledge_base['parameters'].get(param, {})
                normal_min = param_info.get('normal_min', 0)
                normal_max = param_info.get('normal_max', 100)
                unit = param_info.get('unit', '')
                
                if normal_min <= value <= normal_max:
                    status_icon = "✓"
                    status_text = "NORMAL"
                else:
                    status_icon = "⚠"
                    status_text = "ABNORMAL"
                
                answer += f"{status_icon} {param}: {value:.2f} {unit} ({status_text})\n"
        
        return {
            'type': 'analysis',
            'answer': answer,
            'confidence': 0.9,
            'actions': ['monitor_stage']
        }
    
    def _get_stage_status(self, data: Dict, critical_params: List[str]) -> Dict:
        """Get status of a process stage"""
        
        issues = []
        abnormal_count = 0
        
        for param in critical_params:
            if param in data:
                value = data[param]
                param_info = self.knowledge_base['parameters'].get(param, {})
                normal_min = param_info.get('normal_min', 0)
                normal_max = param_info.get('normal_max', 100)
                
                if value < normal_min or value > normal_max:
                    abnormal_count += 1
                    issues.append(f"{param} out of range")
        
        if abnormal_count == 0:
            status = "✓ GOOD"
        elif abnormal_count == 1:
            status = "⚠ WARNING"
        else:
            status = "✗ SEVERE"
        
        return {
            'status': status,
            'issues': issues
        }
    
    def _generate_parameter_recommendation(self, param: str, info: Dict) -> Optional[Dict]:
        """Generate recommendation for a parameter"""
        
        value = info['value']
        normal_min = info['normal_min']
        normal_max = info['normal_max']
        unit = info['unit']
        
        # Determine action
        if value > normal_max:
            action = f"Reduce {param} to bring within normal range"
            target_min = normal_min
            target_max = (normal_min + normal_max) / 2
        elif value < normal_min:
            action = f"Increase {param} to bring within normal range"
            target_min = (normal_min + normal_max) / 2
            target_max = normal_max
        else:
            return None
        
        # Determine priority
        if info['severity'] == 'SEVERE':
            priority = "CRITICAL"
        else:
            priority = "MEDIUM"
        
        return {
            'parameter': param,
            'current': value,
            'target_min': target_min,
            'target_max': target_max,
            'unit': unit,
            'action': action,
            'priority': priority
        }


# Global copilot instance
_copilot_service: Optional[CopilotService] = None


def get_copilot_service() -> CopilotService:
    """
    Get or create copilot service singleton
    
    Returns:
        Copilot service instance
    """
    global _copilot_service
    if _copilot_service is None:
        _copilot_service = CopilotService()
    return _copilot_service


if __name__ == "__main__":
    print("=== Copilot Service Test ===\n")
    
    copilot = get_copilot_service()
    
    # Test queries
    test_queries = [
        "Why is this batch severe?",
        "Analyze wire bonding",
        "How can I improve this process?",
        "Explain die attach stage"
    ]
    
    # Test data (SEVERE condition)
    test_data = {
        'die_temperature': 195.0,
        'die_void_percentage': 6.0,
        'wire_pull_strength': 5.0,
        'wire_bonding_force': 35.0,
        'mold_voids': 2.5,
        'cure_uniformity': 2.8,
        'inspect_reliability_score': 82.0,
        'inspect_defect_count': 3,
        'predicted_status': 'SEVERE'
    }
    
    context = {'current_data': test_data}
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 60)
        response = copilot.process_query(query, context)
        print(f"Type: {response['type']}")
        print(f"Confidence: {response['confidence']:.1%}")
        print(f"\nAnswer:\n{response['answer']}")
        print("=" * 60)
    
    print("\n✓ Copilot service test complete")

# Made with Bob
