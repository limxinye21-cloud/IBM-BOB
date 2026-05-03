**User:**

<task>
Improve the UI to display scenario-specific data and status for the AI Packaging Reliability Dashboard.

**Context:**
The user wants each scenario to display different data and status in the UI. Currently, there are 8 scenarios defined in `data/mock/scenarios.py`:
1. normal - Normal Operation (GOOD status expected)
2. die_attach_drift - Die Attach Temperature Drift (WARNING expected)
3. wire_bonding_failure - Wire Bonding Failure (SEVERE expected)
4. molding_issue - Molding Compound Issue (SEVERE expected)
5. curing_incomplete - Incomplete Curing (SEVERE expected)
6. inspection_failure - Inspection Failure (SEVERE expected)
7. cascading_failure - Cascading Failure (SEVERE expected)
8. intermittent_warning - Intermittent Warnings (WARNING expected)

**Requirements:**
1. Create a new component `frontend/components/scenario_display.py` that:
   - Defines configuration for each scenario (name, icon, color, expected status, description, key parameters to highlight)
   - Provides a function to render scenario-specific information cards
   - Shows scenario name, icon, and description prominently
   - Highlights the key parameters relevant to each scenario
   - Uses color coding based on expected status (green for GOOD, yellow for WARNING, red for SEVERE)

2. Update `frontend/professional_dashboard.py` to:
   - Import and use the new scenario display component
   - Show the current scenario name and description at the top
   - Display scenario-specific alerts/warnings based on the scenario type
   - Highlight the parameters most relevant to the current scenario
   - Use better visual design with cards, colors, and icons

3. Ensure the UI properly renders HTML (not showing HTML code as text) by using `unsafe_allow_html=True` in st.markdown()

4. Make the UI more professional with:
   - Better spacing and layout
   - Clear visual hierarchy
   - Scenario-specific color themes
   - Icons for different scenarios
   - Responsive design

**Files to modify:**
- Create: `frontend/components/scenario_display.py`
- Update: `frontend/professional_dashboard.py`

**Important:** Only perform the work outlined in these instructions. Do not deviate from the scope. When complete, use attempt_completion with a concise summary of changes made.
</task>
<environment_details>
# VSCode Visible Files
..\..\..\AppData\Local\Programs\IBM Bob\scenario_display.py,frontend\components\scenario_display.py

# VSCode Open Tabs
SYSTEM_ARCHITECTURE.md,PROJECT_STRUCTURE.md,ARCHITECTURE_DIAGRAMS.md,IMPLEMENTATION_PLAN.md,STEP1_SUMMARY.md,DATA_SCHEMA.md,STEP2_SUMMARY.md,data/mock/config_schema.py,data/mock/__init__.py,backend/app/config.py,requirements.txt,backend/app/db/__init__.py,backend/app/schemas/data_schema.py,backend/app/schemas/copilot_schema.py,backend/app/api/routes/data.py,backend/app/__init__.py,backend/app/api/__init__.py,backend/app/api/routes/__init__.py,backend/app/schemas/__init__.py,ml/training/features.py

# Actively Running Terminals
## Terminal 1 (Active)
### Working Directory: `c:\Users\ASUS\OneDrive\Desktop\IBM BOB`
### Original command: `.\start_backend.bat`
## Terminal 2 (Active)
### Working Directory: `c:\Users\ASUS\OneDrive\Desktop\IBM BOB`
### Original command: `.\start_dashboard.bat`
## Terminal 3 (Active)
### Working Directory: `c:\Users\ASUS\OneDrive\Desktop\IBM BOB`
### Original command: `curl http://localhost:8000/health`

# Current Time
Current time in ISO 8601 UTC format: 2026-05-03T02:39:08.760Z
User time zone: Asia/Kuala_Lumpur, UTC+8:00

# Current Cost
$0.00

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>code</slug>
<name>💻 Code</name>


# Current Workspace Directory (c:/Users/ASUS/OneDrive/Desktop/IBM BOB) Files
ARCHITECTURE_DIAGRAMS.md
DASHBOARD_QUICKSTART.md
DATA_SCHEMA.md
demo_simulation.py
DEPLOYMENT_GUIDE.md
DEVELOP_BRANCH.md
IBM-Bob-Dev-Day-hackathon-guide.pdf
IMPLEMENTATION_PLAN.md
migrate_db.py
Packaging Reliability Risk Prediction at Micron_ Research Report.pdf
packaging_data.db
PROFESSIONAL_DASHBOARD_README.md
PROJECT_STRUCTURE.md
QUICK_START.md
README.md
requirements.txt
run.py
start_backend.bat
start_dashboard.bat
start_professional_dashboard.bat
STEP1_SUMMARY.md
STEP2_SUMMARY.md
STEP3_SUMMARY.md
STEP5_SUMMARY.md
STEP6_SUMMARY.md
STEP7_SUMMARY.md
STEP8_SUMMARY.md
STEP9_SUMMARY.md
SYSTEM_ARCHITECTURE.md
test_api.py
backend/
backend/app/
backend/app/__init__.py
backend/app/config.py
backend/app/main.py
backend/app/api/
backend/app/api/__init__.py
backend/app/api/routes/
backend/app/api/routes/__init__.py
backend/app/api/routes/alerts.py
backend/app/api/routes/copilot.py
backend/app/api/routes/data.py
backend/app/api/routes/ml.py
backend/app/db/
backend/app/db/__init__.py
backend/app/db/database.py
backend/app/db/models.py
backend/app/models/
backend/app/schemas/
backend/app/schemas/__init__.py
backend/app/schemas/copilot_schema.py
backend/app/schemas/data_schema.py
backend/app/services/
backend/app/services/alert_service.py
backend/app/services/copilot_service.py
backend/app/services/ml_service.py
backend/app/utils/
backend/tests/
data/
data/mock/
data/mock/__init__.py
data/mock/config_schema.py
data/mock/enhanced_config_schema.py
data/mock/generator.py
data/mock/scenarios.py
data/mock/test_generator.py
data/sample/
frontend/
frontend/__init__.py
frontend/dashboard.py
frontend/professional_dashboard.py
frontend/components/
frontend/components/__init__.py
frontend/components/alerts_panel.py
frontend/components/charts.py
frontend/components/chat_copilot.py
frontend/components/scenario_display.py
frontend/components/status_light.py
frontend/utils/
frontend/utils/__init__.py
frontend/utils/api_client.py
logs/
ml/
ml/notebooks/
ml/saved_models/
ml/saved_models/feature_engineer_20260503_003607.joblib
ml/saved_models/feature_engineer_latest.joblib
ml/saved_models/metadata_20260503_003607.json
ml/saved_models/metadata_latest.json
ml/saved_models/model_20260503_003607.joblib
ml/saved_models/model_latest.joblib
ml/training/
ml/training/features.py
ml/training/inference.py
ml/training/physics_features.py
ml/training/train.py
orchestrate/
orchestrate/WATSONX_ORCHESTRATE_INTEGRATION.md
scripts/
scripts/health_check.py
scripts/start_system.py
tests/
tests/test_integration.py
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

I'll help you improve the UI to display scenario-specific data and status for the AI Packaging Reliability Dashboard. Let me start by examining the current files to understand the structure.

<read_file>
<args>
<file>
<path>data/mock/scenarios.py</path>
</file>
<file>
<path>frontend/professional_dashboard.py</path>
</file>
<file>
<path>frontend/components/scenario_display.py</path>
</file>
</args>
</read_file>

---

**User:**

[read_file for 'data/mock/scenarios.py', 'frontend/professional_dashboard.py', 'frontend/components/scenario_display.py'] Result:
<files>
<file><path>data/mock/scenarios.py</path>
<content lines="1-282">
  1 | """
  2 | Predefined Failure Scenarios for Mock Data Generation
  3 | 
  4 | This module defines realistic failure scenarios for testing and demonstration:
  5 | - Normal operation
  6 | - Gradual drift
  7 | - Sudden failures
  8 | - Cross-stage propagation
  9 | """
 10 | 
 11 | from typing import Dict, List, Callable
 12 | from dataclasses import dataclass
 13 | 
 14 | from data.mock.config_schema import ProcessStage, Status
 15 | from data.mock.generator import MockDataGenerator, ProcessData
 16 | 
 17 | 
 18 | @dataclass
 19 | class Scenario:
 20 |     """Scenario definition"""
 21 |     name: str
 22 |     description: str
 23 |     duration: int  # Number of samples
 24 |     setup_func: Callable[[MockDataGenerator], None]
 25 | 
 26 | 
 27 | # ============================================================================
 28 | # SCENARIO DEFINITIONS
 29 | # ============================================================================
 30 | 
 31 | def setup_normal_operation(generator: MockDataGenerator):
 32 |     """Normal operation - all parameters in range"""
 33 |     generator.reset()
 34 | 
 35 | 
 36 | def setup_die_attach_drift(generator: MockDataGenerator):
 37 |     """Gradual temperature drift in die attach"""
 38 |     generator.reset()
 39 |     generator.inject_gradual_drift(ProcessStage.DIE_ATTACH, "temperature", 0.2)
 40 |     generator.inject_gradual_drift(ProcessStage.DIE_ATTACH, "void_percentage", 0.05)
 41 | 
 42 | 
 43 | def setup_wire_bonding_failure(generator: MockDataGenerator):
 44 |     """Sudden wire bonding failure"""
 45 |     generator.reset()
 46 |     generator.inject_sudden_anomaly(ProcessStage.WIRE_BONDING, Status.SEVERE, 3)
 47 | 
 48 | 
 49 | def setup_molding_issue(generator: MockDataGenerator):
 50 |     """Molding compound viscosity issue"""
 51 |     generator.reset()
 52 |     generator.inject_sudden_anomaly(ProcessStage.MOLDING, Status.SEVERE, 2)
 53 | 
 54 | 
 55 | def setup_curing_incomplete(generator: MockDataGenerator):
 56 |     """Incomplete curing due to temperature/time issues"""
 57 |     generator.reset()
 58 |     generator.inject_sudden_anomaly(ProcessStage.CURING, Status.SEVERE, 3)
 59 | 
 60 | 
 61 | def setup_inspection_failure(generator: MockDataGenerator):
 62 |     """Multiple defects detected at inspection"""
 63 |     generator.reset()
 64 |     generator.inject_sudden_anomaly(ProcessStage.INSPECTION, Status.SEVERE, 4)
 65 | 
 66 | 
 67 | def setup_cascading_failure(generator: MockDataGenerator):
 68 |     """
 69 |     Cascading failure: die attach issue propagates through stages
 70 |     This demonstrates cross-stage dependency
 71 |     """
 72 |     generator.reset()
 73 |     # Start with die attach issue
 74 |     generator.inject_sudden_anomaly(ProcessStage.DIE_ATTACH, Status.SEVERE, 2)
 75 | 
 76 | 
 77 | def setup_intermittent_warning(generator: MockDataGenerator):
 78 |     """Intermittent warnings in multiple stages"""
 79 |     generator.reset()
 80 |     generator.inject_sudden_anomaly(ProcessStage.WIRE_BONDING, Status.WARNING, 1)
 81 | 
 82 | 
 83 | # ============================================================================
 84 | # SCENARIO CATALOG
 85 | # ============================================================================
 86 | 
 87 | SCENARIOS = {
 88 |     "normal": Scenario(
 89 |         name="Normal Operation",
 90 |         description="All parameters within normal range, stable production",
 91 |         duration=100,
 92 |         setup_func=setup_normal_operation
 93 |     ),
 94 |     
 95 |     "die_attach_drift": Scenario(
 96 |         name="Die Attach Temperature Drift",
 97 |         description="Gradual temperature increase and void formation in die attach",
 98 |         duration=100,
 99 |         setup_func=setup_die_attach_drift
100 |     ),
101 |     
102 |     "wire_bonding_failure": Scenario(
103 |         name="Wire Bonding Failure",
104 |         description="Sudden failure in wire bonding - force, ultrasonic power issues",
105 |         duration=100,
106 |         setup_func=setup_wire_bonding_failure
107 |     ),
108 |     
109 |     "molding_issue": Scenario(
110 |         name="Molding Compound Issue",
111 |         description="Molding compound viscosity and void formation problems",
112 |         duration=100,
113 |         setup_func=setup_molding_issue
114 |     ),
115 |     
116 |     "curing_incomplete": Scenario(
117 |         name="Incomplete Curing",
118 |         description="Insufficient cure time and temperature issues",
119 |         duration=100,
120 |         setup_func=setup_curing_incomplete
121 |     ),
122 |     
123 |     "inspection_failure": Scenario(
124 |         name="Inspection Failure",
125 |         description="Multiple defects detected, electrical test failure",
126 |         duration=100,
127 |         setup_func=setup_inspection_failure
128 |     ),
129 |     
130 |     "cascading_failure": Scenario(
131 |         name="Cascading Failure",
132 |         description="Die attach issue propagates through wire bonding to final inspection",
133 |         duration=100,
134 |         setup_func=setup_cascading_failure
135 |     ),
136 |     
137 |     "intermittent_warning": Scenario(
138 |         name="Intermittent Warnings",
139 |         description="Occasional warnings in multiple stages, not severe",
140 |         duration=100,
141 |         setup_func=setup_intermittent_warning
142 |     ),
143 | }
144 | 
145 | 
146 | # ============================================================================
147 | # SCENARIO RUNNER
148 | # ============================================================================
149 | 
150 | class ScenarioRunner:
151 |     """Run predefined scenarios"""
152 |     
153 |     def __init__(self, seed: int = 42):
154 |         """
155 |         Initialize scenario runner
156 |         
157 |         Args:
158 |             seed: Random seed for reproducibility
159 |         """
160 |         self.generator = MockDataGenerator(seed=seed)
161 |         self.current_scenario: str | None = None
162 |     
163 |     def list_scenarios(self) -> List[str]:
164 |         """List available scenarios"""
165 |         return list(SCENARIOS.keys())
166 |     
167 |     def get_scenario_info(self, scenario_name: str) -> Scenario:
168 |         """Get scenario information"""
169 |         if scenario_name not in SCENARIOS:
170 |             raise ValueError(f"Unknown scenario: {scenario_name}")
171 |         return SCENARIOS[scenario_name]
172 |     
173 |     def run_scenario(
174 |         self,
175 |         scenario_name: str,
176 |         num_samples: int | None = None
177 |     ) -> List[ProcessData]:
178 |         """
179 |         Run a specific scenario
180 |         
181 |         Args:
182 |             scenario_name: Name of the scenario to run
183 |             num_samples: Number of samples (None = use scenario default)
184 |             
185 |         Returns:
186 |             List of generated ProcessData
187 |         """
188 |         if scenario_name not in SCENARIOS:
189 |             raise ValueError(f"Unknown scenario: {scenario_name}")
190 |         
191 |         scenario = SCENARIOS[scenario_name]
192 |         self.current_scenario = scenario_name
193 |         
194 |         # Setup scenario
195 |         scenario.setup_func(self.generator)
196 |         
197 |         # Generate data
198 |         duration = num_samples if num_samples is not None else scenario.duration
199 |         batch_data = []
200 |         
201 |         for i in range(duration):
202 |             if self.generator.anomaly_active:
203 |                 data = self.generator.generate_anomaly_data()
204 |             else:
205 |                 data = self.generator.generate_normal_data()
206 |             batch_data.append(data)
207 |         
208 |         return batch_data
209 |     
210 |     def run_demo_sequence(self) -> Dict[str, List[ProcessData]]:
211 |         """
212 |         Run a sequence of scenarios for demo purposes
213 |         
214 |         Returns:
215 |             Dictionary mapping scenario names to data
216 |         """
217 |         demo_scenarios = [
218 |             ("normal", 50),
219 |             ("wire_bonding_failure", 30),
220 |             ("normal", 20),
221 |             ("die_attach_drift", 40),
222 |             ("molding_issue", 30),
223 |         ]
224 |         
225 |         results = {}
226 |         for scenario_name, num_samples in demo_scenarios:
227 |             print(f"Running scenario: {scenario_name} ({num_samples} samples)")
228 |             data = self.run_scenario(scenario_name, num_samples)
229 |             results[scenario_name] = data
230 |         
231 |         return results
232 | 
233 | 
234 | # ============================================================================
235 | # MAIN - Test scenarios
236 | # ============================================================================
237 | 
238 | if __name__ == "__main__":
239 |     print("=== Scenario Runner Test ===\n")
240 |     
241 |     runner = ScenarioRunner(seed=42)
242 |     
243 |     # List scenarios
244 |     print("Available scenarios:")
245 |     for i, scenario_name in enumerate(runner.list_scenarios(), 1):
246 |         scenario = runner.get_scenario_info(scenario_name)
247 |         print(f"{i}. {scenario.name}")
248 |         print(f"   {scenario.description}")
249 |         print()
250 |     
251 |     # Run normal scenario
252 |     print("\n1. Running 'normal' scenario (10 samples)...")
253 |     data = runner.run_scenario("normal", 10)
254 |     status_counts = {"GOOD": 0, "WARNING": 0, "SEVERE": 0}
255 |     for d in data:
256 |         status_counts[d.status] += 1
257 |     print(f"   GOOD: {status_counts['GOOD']}, WARNING: {status_counts['WARNING']}, SEVERE: {status_counts['SEVERE']}")
258 |     
259 |     # Run wire bonding failure
260 |     print("\n2. Running 'wire_bonding_failure' scenario (10 samples)...")
261 |     data = runner.run_scenario("wire_bonding_failure", 10)
262 |     status_counts = {"GOOD": 0, "WARNING": 0, "SEVERE": 0}
263 |     for d in data:
264 |         status_counts[d.status] += 1
265 |     print(f"   GOOD: {status_counts['GOOD']}, WARNING: {status_counts['WARNING']}, SEVERE: {status_counts['SEVERE']}")
266 |     
267 |     # Run die attach drift
268 |     print("\n3. Running 'die_attach_drift' scenario (20 samples)...")
269 |     data = runner.run_scenario("die_attach_drift", 20)
270 |     status_counts = {"GOOD": 0, "WARNING": 0, "SEVERE": 0}
271 |     for d in data:
272 |         status_counts[d.status] += 1
273 |     print(f"   GOOD: {status_counts['GOOD']}, WARNING: {status_counts['WARNING']}, SEVERE: {status_counts['SEVERE']}")
274 |     
275 |     # Show parameter evolution
276 |     print("\n4. Parameter evolution in die_attach_drift:")
277 |     for i, d in enumerate(data[::5]):  # Every 5th sample
278 |         print(f"   Sample {i*5}: Temp={d.die_temperature:.1f}°C, Voids={d.die_void_percentage:.2f}%")
279 |     
280 |     print("\n=== Test Complete ===")
281 | 
282 | # Made with Bob
</content>
</file>
<file><path>frontend/professional_dashboard.py</path>
<content lines="1-425">
  1 | """
  2 | Professional AI Packaging Reliability Risk Prediction Dashboard
  3 | Based on Micron Research Implementation
  4 | Real-time semiconductor packaging monitoring with ML-powered risk assessment
  5 | """
  6 | 
  7 | import streamlit as st
  8 | import pandas as pd
  9 | import plotly.graph_objects as go
 10 | import plotly.express as px
 11 | from plotly.subplots import make_subplots
 12 | import time
 13 | from datetime import datetime, timedelta
 14 | import sys
 15 | import os
 16 | import numpy as np
 17 | 
 18 | # Add project root to path
 19 | sys.path.append(os.path.dirname(os.path.dirname(__file__)))
 20 | 
 21 | from frontend.utils.api_client import get_api_client
 22 | from data.mock.generator import MockDataGenerator
 23 | from data.mock.scenarios import SCENARIOS
 24 | 
 25 | # Page configuration
 26 | st.set_page_config(
 27 |     page_title="Packaging Reliability Risk Prediction",
 28 |     page_icon="🔬",
 29 |     layout="wide",
 30 |     initial_sidebar_state="collapsed"
 31 | )
 32 | 
 33 | # Professional CSS Styling
 34 | st.markdown("""
 35 | <style>
 36 |     .main {
 37 |         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
 38 |         padding: 0;
 39 |     }
 40 |     
 41 |     .header-container {
 42 |         background: white;
 43 |         padding: 20px 40px;
 44 |         border-bottom: 3px solid #667eea;
 45 |         margin-bottom: 20px;
 46 |     }
 47 |     
 48 |     .main-title {
 49 |         font-size: 32px;
 50 |         font-weight: 700;
 51 |         color: #1a1a1a;
 52 |         margin: 0;
 53 |     }
 54 |     
 55 |     .subtitle {
 56 |         font-size: 14px;
 57 |         color: #666;
 58 |         margin-top: 5px;
 59 |     }
 60 |     
 61 |     .metric-card {
 62 |         background: white;
 63 |         border-radius: 12px;
 64 |         padding: 20px;
 65 |         box-shadow: 0 4px 6px rgba(0,0,0,0.1);
 66 |         margin-bottom: 20px;
 67 |     }
 68 |     
 69 |     .risk-indicator {
 70 |         display: inline-block;
 71 |         padding: 8px 16px;
 72 |         border-radius: 20px;
 73 |         font-weight: 600;
 74 |         font-size: 14px;
 75 |     }
 76 |     
 77 |     .risk-good { background: #10b981; color: white; }
 78 |     .risk-warning { background: #f59e0b; color: white; }
 79 |     .risk-severe { background: #ef4444; color: white; }
 80 |     
 81 |     .status-badge {
 82 |         display: inline-block;
 83 |         padding: 6px 12px;
 84 |         border-radius: 12px;
 85 |         font-size: 12px;
 86 |         font-weight: 600;
 87 |         margin-left: 10px;
 88 |     }
 89 |     
 90 |     .status-idle { background: #e5e7eb; color: #6b7280; }
 91 |     .status-running {
 92 |         background: #10b981;
 93 |         color: white;
 94 |         animation: pulse 2s infinite;
 95 |     }
 96 |     
 97 |     @keyframes pulse {
 98 |         0%, 100% { opacity: 1; }
 99 |         50% { opacity: 0.7; }
100 |     }
101 |     
102 |     .stButton>button {
103 |         border-radius: 8px;
104 |         height: 50px;
105 |         font-weight: 600;
106 |         font-size: 16px;
107 |     }
108 | </style>
109 | """, unsafe_allow_html=True)
110 | 
111 | # Initialize session state
112 | if 'monitoring_active' not in st.session_state:
113 |     st.session_state.monitoring_active = False
114 | if 'current_data' not in st.session_state:
115 |     st.session_state.current_data = None
116 | if 'prediction_result' not in st.session_state:
117 |     st.session_state.prediction_result = None
118 | if 'data_history' not in st.session_state:
119 |     st.session_state.data_history = []
120 | if 'mock_generator' not in st.session_state:
121 |     st.session_state.mock_generator = MockDataGenerator()
122 | if 'api_client' not in st.session_state:
123 |     st.session_state.api_client = get_api_client()
124 | if 'show_data_panel' not in st.session_state:
125 |     st.session_state.show_data_panel = True
126 | if 'selected_scenario' not in st.session_state:
127 |     st.session_state.selected_scenario = "normal"
128 | 
129 | 
130 | def main():
131 |     """Main application"""
132 |     # Header
133 |     st.markdown("""
134 |     <div class="header-container">
135 |         <div class="main-title">🔬 Packaging Reliability Risk Prediction System</div>
136 |         <div class="subtitle">Real-time AI-powered semiconductor packaging quality monitoring | Micron Technology</div>
137 |     </div>
138 |     """, unsafe_allow_html=True)
139 |     
140 |     # Control Panel
141 |     render_control_panel()
142 |     
143 |     st.markdown("---")
144 |     
145 |     # Data Loading Panel (Collapsible)
146 |     render_data_loading_panel()
147 |     
148 |     st.markdown("---")
149 |     
150 |     # Auto-generate data if monitoring is active
151 |     if st.session_state.monitoring_active:
152 |         generate_and_predict()
153 |         time.sleep(2)  # Sampling rate
154 |         st.rerun()
155 |     
156 |     # Main Dashboard
157 |     render_risk_dashboard()
158 |     
159 |     # Process Parameters
160 |     if st.session_state.current_data:
161 |         st.markdown("---")
162 |         render_process_parameters()
163 |         
164 |         st.markdown("---")
165 |         render_trend_charts()
166 | 
167 | 
168 | def render_control_panel():
169 |     """Render main control panel"""
170 |     col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
171 |     
172 |     with col1:
173 |         st.markdown("### 🎛️ Monitoring Controls")
174 |         status = "RUNNING" if st.session_state.monitoring_active else "IDLE"
175 |         status_class = "status-running" if st.session_state.monitoring_active else "status-idle"
176 |         st.markdown(f'<span class="status-badge {status_class}">{status}</span>', unsafe_allow_html=True)
177 |     
178 |     with col2:
179 |         if not st.session_state.monitoring_active:
180 |             if st.button("▶️ START PREDICTION", type="primary", use_container_width=True):
181 |                 st.session_state.monitoring_active = True
182 |                 st.rerun()
183 |     
184 |     with col3:
185 |         if st.session_state.monitoring_active:
186 |             if st.button("⏸️ STOP", use_container_width=True):
187 |                 st.session_state.monitoring_active = False
188 |                 st.rerun()
189 |     
190 |     with col4:
191 |         if st.button("🔄 RESET", use_container_width=True):
192 |             st.session_state.monitoring_active = False
193 |             st.session_state.current_data = None
194 |             st.session_state.prediction_result = None
195 |             st.session_state.data_history = []
196 |             st.rerun()
197 | 
198 | 
199 | def render_data_loading_panel():
200 |     """Render collapsible data loading panel"""
201 |     col1, col2 = st.columns([6, 1])
202 |     with col1:
203 |         st.markdown("### 📊 Data Configuration")
204 |     with col2:
205 |         if st.button("▼" if st.session_state.show_data_panel else "▶", key="toggle_panel"):
206 |             st.session_state.show_data_panel = not st.session_state.show_data_panel
207 |             st.rerun()
208 |     
209 |     if st.session_state.show_data_panel:
210 |         col1, col2, col3 = st.columns(3)
211 |         
212 |         with col1:
213 |             st.markdown("**Data Source**")
214 |             data_source = st.selectbox(
215 |                 "source",
216 |                 ["Mock Generator", "Live Sensor Feed", "Historical Data"],
217 |                 label_visibility="collapsed"
218 |             )
219 |         
220 |         with col2:
221 |             st.markdown("**Scenario**")
222 |             scenario_options = ["normal"] + list(SCENARIOS.keys())
223 |             st.session_state.selected_scenario = st.selectbox(
224 |                 "scenario",
225 |                 scenario_options,
226 |                 label_visibility="collapsed"
227 |             )
228 |         
229 |         with col3:
230 |             st.markdown("**Sampling Rate**")
231 |             st.select_slider(
232 |                 "rate",
233 |                 options=[0.5, 1, 2, 3, 5],
234 |                 value=2,
235 |                 label_visibility="collapsed"
236 |             )
237 | 
238 | 
239 | def generate_and_predict():
240 |     """Generate data and get prediction"""
241 |     generator = st.session_state.mock_generator
242 |     api_client = st.session_state.api_client
243 |     
244 |     # Generate data
245 |     if st.session_state.selected_scenario != "normal":
246 |         scenario_config = SCENARIOS.get(st.session_state.selected_scenario)
247 |         data = generator.generate_single(scenario=scenario_config)
248 |     else:
249 |         data = generator.generate_single()
250 |     
251 |     data_dict = data.to_dict()
252 |     st.session_state.current_data = data_dict
253 |     
254 |     # Get prediction
255 |     result = api_client.predict(data_dict)
256 |     
257 |     if result.get('success'):
258 |         st.session_state.prediction_result = result['prediction']
259 |         st.session_state.data_history.append({
260 |             'timestamp': datetime.now(),
261 |             'status': result['prediction']['status'],
262 |             'confidence': result['prediction']['confidence'],
263 |             'data': data_dict
264 |         })
265 |         if len(st.session_state.data_history) > 50:
266 |             st.session_state.data_history = st.session_state.data_history[-50:]
267 | 
268 | 
269 | def render_risk_dashboard():
270 |     """Render risk dashboard"""
271 |     if st.session_state.prediction_result is None:
272 |         st.info("👆 Click START PREDICTION to begin monitoring")
273 |         return
274 |     
275 |     pred = st.session_state.prediction_result
276 |     data = st.session_state.current_data
277 |     
278 |     col1, col2, col3, col4 = st.columns(4)
279 |     
280 |     with col1:
281 |         status = pred['status']
282 |         confidence = pred['confidence']
283 |         risk_class = {'GOOD': 'risk-good', 'WARNING': 'risk-warning', 'SEVERE': 'risk-severe'}.get(status, 'risk-good')
284 |         
285 |         st.markdown(f"""
286 |         <div class="metric-card">
287 |             <div style="font-size: 14px; color: #6b7280; margin-bottom: 8px;">RISK STATUS</div>
288 |             <div class="risk-indicator {risk_class}">{status}</div>
289 |             <div style="font-size: 24px; font-weight: 700; margin-top: 12px;">{confidence*100:.1f}%</div>
290 |             <div style="font-size: 12px; color: #6b7280;">Confidence</div>
291 |         </div>
292 |         """, unsafe_allow_html=True)
293 |     
294 |     with col2:
295 |         st.markdown(f"""
296 |         <div class="metric-card">
297 |             <div style="font-size: 14px; color: #6b7280; margin-bottom: 8px;">BATCH ID</div>
298 |             <div style="font-size: 20px; font-weight: 600;">{data.get('batch_id', 'N/A')}</div>
299 |             <div style="font-size: 12px; color: #6b7280; margin-top: 12px;">Machine: {data.get('machine_id', 'N/A')}</div>
300 |         </div>
301 |         """, unsafe_allow_html=True)
302 |     
303 |     with col3:
304 |         defect_count = data.get('inspect_defect_count', 0)
305 |         reliability = data.get('inspect_reliability_score', 0)
306 |         st.markdown(f"""
307 |         <div class="metric-card">
308 |             <div style="font-size: 14px; color: #6b7280; margin-bottom: 8px;">QUALITY METRICS</div>
309 |             <div style="font-size: 24px; font-weight: 700;">{defect_count}</div>
310 |             <div style="font-size: 12px; color: #6b7280;">Defects | Reliability: {reliability:.1f}%</div>
311 |         </div>
312 |         """, unsafe_allow_html=True)
313 |     
314 |     with col4:
315 |         history_count = len(st.session_state.data_history)
316 |         severe_rate = 0
317 |         if history_count > 0:
318 |             severe_count = sum(1 for h in st.session_state.data_history if h['status'] == 'SEVERE')
319 |             severe_rate = (severe_count / history_count) * 100
320 |         
321 |         st.markdown(f"""
322 |         <div class="metric-card">
323 |             <div style="font-size: 14px; color: #6b7280; margin-bottom: 8px;">BATCH STATISTICS</div>
324 |             <div style="font-size: 24px; font-weight: 700;">{history_count}</div>
325 |             <div style="font-size: 12px; color: #6b7280;">Samples | Severe: {severe_rate:.1f}%</div>
326 |         </div>
327 |         """, unsafe_allow_html=True)
328 | 
329 | 
330 | def render_process_parameters():
331 |     """Render process parameters"""
332 |     data = st.session_state.current_data
333 |     st.markdown("### 🔧 Critical Process Parameters")
334 |     
335 |     tab1, tab2, tab3, tab4, tab5 = st.tabs(["Die Attach", "Wire Bonding", "Molding", "Curing", "Inspection"])
336 |     
337 |     with tab1:
338 |         cols = st.columns(4)
339 |         cols[0].metric("Temperature", f"{data.get('die_temperature', 0):.1f}°C", "±2°C")
340 |         cols[1].metric("Void %", f"{data.get('die_void_percentage', 0):.2f}%", "Target <3%")
341 |         cols[2].metric("Placement", f"{data.get('die_placement_accuracy', 0):.1f}μm", "Target <10μm")
342 |         cols[3].metric("Bond Line", f"{data.get('die_bond_line_thickness', 0):.1f}μm", "20-30μm")
343 |     
344 |     with tab2:
345 |         cols = st.columns(4)
346 |         cols[0].metric("Bond Force", f"{data.get('wire_bonding_force', 0):.1f}N", "35-55N")
347 |         cols[1].metric("Ultrasonic", f"{data.get('wire_ultrasonic_power', 0):.1f}mW", "70-110mW")
348 |         cols[2].metric("Loop Height", f"{data.get('wire_loop_height', 0):.1f}μm", "200-250μm")
349 |         cols[3].metric("Pull Strength", f"{data.get('wire_pull_strength', 0):.1f}gf", ">8gf")
350 |     
351 |     with tab3:
352 |         cols = st.columns(4)
353 |         cols[0].metric("Mold Temp", f"{data.get('mold_temperature', 0):.1f}°C", "165-185°C")
354 |         cols[1].metric("Pressure", f"{data.get('mold_pressure', 0):.1f}MPa", "5-9MPa")
355 |         cols[2].metric("Fill Time", f"{data.get('mold_fill_time', 0):.1f}s", "3-5s")
356 |         cols[3].metric("Voids", f"{data.get('mold_voids', 0):.2f}%", "Target <1%")
357 |     
358 |     with tab4:
359 |         cols = st.columns(4)
360 |         cols[0].metric("Cure Temp", f"{data.get('cure_temperature', 0):.1f}°C", "170-190°C")
361 |         cols[1].metric("Cure Time", f"{data.get('cure_time', 0):.0f}min", "120-180min")
362 |         cols[2].metric("Humidity", f"{data.get('cure_humidity', 0):.1f}%", "30-50%")
363 |         cols[3].metric("Uniformity", f"{data.get('cure_uniformity', 0):.2f}°C", "Target <2°C")
364 |     
365 |     with tab5:
366 |         cols = st.columns(4)
367 |         cols[0].metric("Defects", f"{data.get('inspect_defect_count', 0)}", "Target 0")
368 |         cols[1].metric("Visual Score", f"{data.get('inspect_visual_score', 0):.1f}", ">90")
369 |         cols[2].metric("Electrical", "PASS" if data.get('inspect_electrical_test', 1) == 1 else "FAIL")
370 |         cols[3].metric("Reliability", f"{data.get('inspect_reliability_score', 0):.1f}%", ">95%")
371 | 
372 | 
373 | def render_trend_charts():
374 |     """Render trend charts"""
375 |     if len(st.session_state.data_history) < 2:
376 |         return
377 |     
378 |     st.markdown("### 📈 Real-Time Trends")
379 |     
380 |     # Prepare data
381 |     df = pd.DataFrame([
382 |         {
383 |             'timestamp': h['timestamp'],
384 |             'status': h['status'],
385 |             'confidence': h['confidence']
386 |         }
387 |         for h in st.session_state.data_history
388 |     ])
389 |     
390 |     col1, col2 = st.columns(2)
391 |     
392 |     with col1:
393 |         # Confidence trend
394 |         fig = go.Figure()
395 |         fig.add_trace(go.Scatter(
396 |             x=df['timestamp'],
397 |             y=df['confidence'] * 100,
398 |             mode='lines+markers',
399 |             name='Confidence',
400 |             line=dict(color='#667eea', width=2)
401 |         ))
402 |         fig.update_layout(
403 |             title="Prediction Confidence Over Time",
404 |             xaxis_title="Time",
405 |             yaxis_title="Confidence (%)",
406 |             height=300
407 |         )
408 |         st.plotly_chart(fig, use_container_width=True)
409 |     
410 |     with col2:
411 |         # Status distribution
412 |         status_counts = df['status'].value_counts()
413 |         fig = go.Figure(data=[go.Pie(
414 |             labels=status_counts.index,
415 |             values=status_counts.values,
416 |             marker=dict(colors=['#10b981', '#f59e0b', '#ef4444'])
417 |         )])
418 |         fig.update_layout(title="Status Distribution", height=300)
419 |         st.plotly_chart(fig, use_container_width=True)
420 | 
421 | 
422 | if __name__ == "__main__":
423 |     main()
424 | 
425 | # Made with Bob
</content>
</file>
<file><path>frontend/components/scenario_display.py</path>
<content/><notice>File is empty</notice>
</file>
</files>
<environment_details>
# VSCode Visible Files
..\..\..\AppData\Local\Programs\IBM Bob\scenario_display.py,frontend\components\scenario_display.py

# VSCode Open Tabs
SYSTEM_ARCHITECTURE.md,PROJECT_STRUCTURE.md,ARCHITECTURE_DIAGRAMS.md,IMPLEMENTATION_PLAN.md,STEP1_SUMMARY.md,DATA_SCHEMA.md,STEP2_SUMMARY.md,data/mock/config_schema.py,data/mock/__init__.py,backend/app/config.py,requirements.txt,backend/app/db/__init__.py,backend/app/schemas/data_schema.py,backend/app/schemas/copilot_schema.py,backend/app/api/routes/data.py,backend/app/__init__.py,backend/app/api/__init__.py,backend/app/api/routes/__init__.py,backend/app/schemas/__init__.py,ml/training/features.py

# Actively Running Terminals
## Terminal 1 (Active)
### Working Directory: `c:\Users\ASUS\OneDrive\Desktop\IBM BOB`
### Original command: `.\start_backend.bat`
## Terminal 2 (Active)
### Working Directory: `c:\Users\ASUS\OneDrive\Desktop\IBM BOB`
### Original command: `.\start_dashboard.bat`
## Terminal 3 (Active)
### Working Directory: `c:\Users\ASUS\OneDrive\Desktop\IBM BOB`
### Original command: `curl http://localhost:8000/health`

# Current Time
Current time in ISO 8601 UTC format: 2026-05-03T02:39:18.213Z
User time zone: Asia/Kuala_Lumpur, UTC+8:00

# Current Cost
$0.01

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>code</slug>
<name>💻 Code</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

I'll create a comprehensive scenario display component and update the professional dashboard to show scenario-specific data and status. Let me start by creating a todo list for this task.

<update_todo_list>
<todos>
[ ] Create scenario_display.py component with scenario configurations
[ ] Update professional_dashboard.py to integrate scenario display
[ ] Test the implementation
</todos>
</update_todo_list>

---

**User:**

[update_todo_list] Result:
Todo list updated successfully.
<environment_details>
# VSCode Visible Files
..\..\..\AppData\Local\Programs\IBM Bob\scenario_display.py,frontend\components\scenario_display.py

# VSCode Open Tabs
SYSTEM_ARCHITECTURE.md,PROJECT_STRUCTURE.md,ARCHITECTURE_DIAGRAMS.md,IMPLEMENTATION_PLAN.md,STEP1_SUMMARY.md,DATA_SCHEMA.md,STEP2_SUMMARY.md,data/mock/config_schema.py,data/mock/__init__.py,backend/app/config.py,requirements.txt,backend/app/db/__init__.py,backend/app/schemas/data_schema.py,backend/app/schemas/copilot_schema.py,backend/app/api/routes/data.py,backend/app/__init__.py,backend/app/api/__init__.py,backend/app/api/routes/__init__.py,backend/app/schemas/__init__.py,ml/training/features.py

# Actively Running Terminals
## Terminal 1 (Active)
### Working Directory: `c:\Users\ASUS\OneDrive\Desktop\IBM BOB`
### Original command: `.\start_backend.bat`
## Terminal 2 (Active)
### Working Directory: `c:\Users\ASUS\OneDrive\Desktop\IBM BOB`
### Original command: `.\start_dashboard.bat`
## Terminal 3 (Active)
### Working Directory: `c:\Users\ASUS\OneDrive\Desktop\IBM BOB`
### Original command: `curl http://localhost:8000/health`

# Current Time
Current time in ISO 8601 UTC format: 2026-05-03T02:39:29.163Z
User time zone: Asia/Kuala_Lumpur, UTC+8:00

# Current Cost
$0.05

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>code</slug>
<name>💻 Code</name>
====

REMINDERS

Below is your current list of reminders for this task. Keep them updated as you progress.

| # | Content | Status |
|---|---------|--------|
| 1 | Create scenario_display.py component with scenario configurations | Pending |
| 2 | Update professional_dashboard.py to integrate scenario display | Pending |
| 3 | Test the implementation | Pending |


IMPORTANT: When task status changes, remember to call the `update_todo_list` tool to update your progress.

</environment_details>

---

**Assistant:**

Now I'll create the scenario display component with comprehensive scenario configurations.

<write_to_file>
<path>frontend/components/scenario_display.py</path>
<content>"""
Scenario Display Component
Provides scenario-specific UI

[Response interrupted by a tool use result. Only one tool may be used at a time and should be placed at the end of the message.]

---

**User:**

[write_to_file for 'frontend/components/scenario_display.py'] Result:
The tool execution failed with the following error:
<error>
Tool "write_to_file" is not allowed in orchestrator mode.
</error>
<environment_details>
# VSCode Visible Files
..\..\..\AppData\Local\Programs\IBM Bob\scenario_display.py,frontend\components\scenario_display.py

# VSCode Open Tabs
SYSTEM_ARCHITECTURE.md,PROJECT_STRUCTURE.md,ARCHITECTURE_DIAGRAMS.md,IMPLEMENTATION_PLAN.md,STEP1_SUMMARY.md,DATA_SCHEMA.md,STEP2_SUMMARY.md,data/mock/config_schema.py,data/mock/__init__.py,backend/app/config.py,requirements.txt,backend/app/db/__init__.py,backend/app/schemas/data_schema.py,backend/app/schemas/copilot_schema.py,backend/app/api/routes/data.py,backend/app/__init__.py,backend/app/api/__init__.py,backend/app/api/routes/__init__.py,backend/app/schemas/__init__.py,ml/training/features.py

# Actively Running Terminals
## Terminal 1 (Active)
### Working Directory: `c:\Users\ASUS\OneDrive\Desktop\IBM BOB`
### Original command: `.\start_backend.bat`
## Terminal 2 (Active)
### Working Directory: `c:\Users\ASUS\OneDrive\Desktop\IBM BOB`
### Original command: `.\start_dashboard.bat`
## Terminal 3 (Active)
### Working Directory: `c:\Users\ASUS\OneDrive\Desktop\IBM BOB`
### Original command: `curl http://localhost:8000/health`

# Current Time
Current time in ISO 8601 UTC format: 2026-05-03T02:39:40.681Z
User time zone: Asia/Kuala_Lumpur, UTC+8:00

# Current Cost
$0.05

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>orchestrator</slug>
<name>🔀 Orchestrator</name>
====

REMINDERS

Below is your current list of reminders for this task. Keep them updated as you progress.

| # | Content | Status |
|---|---------|--------|
| 1 | Create scenario_display.py component with scenario configurations | Pending |
| 2 | Update professional_dashboard.py to integrate scenario display | Pending |
| 3 | Test the implementation | Pending |


IMPORTANT: When task status changes, remember to call the `update_todo_list` tool to update your progress.

</environment_details>

---

**Assistant:**

I need to switch to Code mode to perform the file modifications. Let me delegate this task to Code mode.

<new_task>
<mode>code</mode>
<message>Improve the UI to display scenario-specific data and status for the AI Packaging Reliability Dashboard.

**Context:**
The user wants each scenario to display different data and status in the UI. Currently, there are 8 scenarios defined in `data/mock/scenarios.py`:
1. normal - Normal Operation (GOOD status expected)
2. die_attach_drift - Die Attach Temperature Drift (WARNING expected)
3. wire_bonding_failure - Wire Bonding Failure (SEVERE expected)
4. molding_issue - Molding Compound Issue (SEVERE expected)
5. curing_incomplete - Incomplete Curing (SEVERE expected)
6. inspection_failure - Inspection Failure (SEVERE expected)
7. cascading_failure - Cascading Failure (SEVERE expected)
8. intermittent_warning - Intermittent Warnings (WARNING expected)

**Requirements:**
1. Create a new component `frontend/components/scenario_display.py` that:
   - Defines configuration for each scenario (name, icon, color, expected status, description, key parameters to highlight)
   - Provides a function to render scenario-specific information cards
   - Shows scenario name, icon, and description prominently
   - Highlights the key parameters relevant to each scenario
   - Uses color coding based on expected status (green for GOOD, yellow for WARNING, red for SEVERE)

2. Update `frontend/professional_dashboard.py` to:
   - Import and use the new scenario display component
   - Show the current scenario name and description at the top
   - Display scenario-specific alerts/warnings based on the scenario type
   - Highlight the parameters most relevant to the current scenario
   - Use better visual design with cards, colors, and icons

3. Ensure the UI properly renders HTML (not showing HTML code as text) by using `unsafe_allow_html=True` in st.markdown()

4. Make the UI more professional with:
   - Better spacing and layout
   - Clear visual hierarchy
   - Scenario-specific color themes
   - Icons for different scenarios
   - Responsive design

**Files to modify:**
- Create: `frontend/components/scenario_display.py`
- Update: `frontend/professional_dashboard.py`

**Important:** Only perform the work outlined in these instructions. Do not deviate from the scope. When complete, use attempt_completion with a concise summary of changes made.</message>
</new_task>

