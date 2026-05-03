"""
AI Copilot Service for AI Packaging Reliability Copilot
Enhanced with stage health scoring, trend analysis, forecasting, and richer responses.

watsonx.ai Integration (optional):
    Set WATSONX_API_KEY and WATSONX_PROJECT_ID environment variables to enable
    IBM Granite model inference for richer NL responses.
    Falls back to rule-based engine when credentials are absent.
"""

import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json

from backend.app.services.ml_service import get_ml_service
from data.mock.config_schema import CROSS_STAGE_DEPENDENCIES

# --------------------------------------------------------------------------- #
# watsonx.ai optional integration stub
# --------------------------------------------------------------------------- #
_WATSONX_API_KEY     = os.environ.get("WATSONX_API_KEY", "")
_WATSONX_PROJECT_ID  = os.environ.get("WATSONX_PROJECT_ID", "")
_WATSONX_URL         = os.environ.get("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
_WATSONX_MODEL       = os.environ.get("WATSONX_MODEL", "ibm/granite-13b-instruct-v2")
_WATSONX_ENABLED     = bool(_WATSONX_API_KEY and _WATSONX_PROJECT_ID)

def _watsonx_generate(prompt: str, max_tokens: int = 400) -> Optional[str]:
    """
    Call IBM watsonx.ai Granite model for NL generation.
    Returns None if watsonx.ai is not configured (falls back to rule-based engine).
    
    To enable: set WATSONX_API_KEY and WATSONX_PROJECT_ID environment variables.
    Model: ibm/granite-13b-instruct-v2 (IBM Granite, recommended for manufacturing Q&A)
    """
    if not _WATSONX_ENABLED:
        return None
    try:
        import requests
        # Step 1: Get IAM token
        iam_resp = requests.post(
            "https://iam.cloud.ibm.com/identity/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=f"grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey={_WATSONX_API_KEY}",
            timeout=10
        )
        iam_token = iam_resp.json().get("access_token", "")
        if not iam_token:
            return None
        # Step 2: Generate
        resp = requests.post(
            f"{_WATSONX_URL}/ml/v1/text/generation?version=2023-05-29",
            headers={"Authorization": f"Bearer {iam_token}", "Content-Type": "application/json"},
            json={
                "model_id": _WATSONX_MODEL,
                "input": prompt,
                "parameters": {"decoding_method": "greedy", "max_new_tokens": max_tokens, "stop_sequences": ["###"]},
                "project_id": _WATSONX_PROJECT_ID
            },
            timeout=20
        )
        result = resp.json()
        return result.get("results", [{}])[0].get("generated_text", "").strip() or None
    except Exception:
        return None

# --------------------------------------------------------------------------- #
# Domain knowledge constants
# --------------------------------------------------------------------------- #

# Normal ranges for every parameter (min, max, unit, description)
PARAM_META: Dict[str, Dict] = {
    "die_temperature":            {"min": 178, "max": 192, "unit": "°C",  "desc": "Die attach temperature"},
    "die_epoxy_temperature":      {"min": 150, "max": 160, "unit": "°C",  "desc": "Epoxy dispense temperature"},
    "die_void_percentage":        {"min": 0,   "max": 3,   "unit": "%",   "desc": "Die-attach void fraction"},
    "die_placement_accuracy":     {"min": 0,   "max": 10,  "unit": "μm",  "desc": "Die placement offset"},
    "die_bond_line_thickness":    {"min": 22,  "max": 28,  "unit": "μm",  "desc": "Bond-line thickness"},
    "die_cure_time":              {"min": 70,  "max": 90,  "unit": "s",   "desc": "Die-cure dwell time"},
    "die_pressure":               {"min": 0.6, "max": 1.0, "unit": "MPa", "desc": "Die-attach pressure"},
    "wire_bonding_force":         {"min": 40,  "max": 52,  "unit": "gf",  "desc": "Bond force"},
    "wire_ultrasonic_power":      {"min": 85,  "max": 100, "unit": "mW",  "desc": "Ultrasonic power"},
    "wire_loop_height":           {"min": 215, "max": 240, "unit": "μm",  "desc": "Wire loop height"},
    "wire_pull_strength":         {"min": 8,   "max": 15,  "unit": "gf",  "desc": "Wire pull strength"},
    "wire_bonding_temperature":   {"min": 160, "max": 170, "unit": "°C",  "desc": "Bonding stage temperature"},
    "wire_diameter":              {"min": 24,  "max": 26,  "unit": "μm",  "desc": "Wire diameter"},
    "wire_bond_time":             {"min": 18,  "max": 24,  "unit": "ms",  "desc": "Bond dwell time"},
    "mold_temperature":           {"min": 172, "max": 180, "unit": "°C",  "desc": "Mold tool temperature"},
    "mold_pressure":              {"min": 6.5, "max": 7.8, "unit": "MPa", "desc": "Transfer mold pressure"},
    "mold_fill_time":             {"min": 3.5, "max": 5.0, "unit": "s",   "desc": "Cavity fill time"},
    "mold_compound_viscosity":    {"min": 115, "max": 140, "unit": "Pa·s","desc": "Compound viscosity"},
    "mold_transfer_speed":        {"min": 11,  "max": 14,  "unit": "mm/s","desc": "Plunger transfer speed"},
    "mold_clamp_force":           {"min": 55,  "max": 68,  "unit": "kN",  "desc": "Clamp force"},
    "mold_voids":                 {"min": 0,   "max": 1.0, "unit": "%",   "desc": "Mold void fraction"},
    "cure_temperature":           {"min": 178, "max": 184, "unit": "°C",  "desc": "Cure oven temperature"},
    "cure_time":                  {"min": 140, "max": 165, "unit": "min", "desc": "Cure dwell time"},
    "cure_humidity":              {"min": 35,  "max": 50,  "unit": "%RH", "desc": "Cure chamber humidity"},
    "cure_thermal_profile":       {"min": 2.5, "max": 3.8, "unit": "°C/min","desc": "Ramp rate"},
    "cure_uniformity":            {"min": 0.5, "max": 2.0, "unit": "°C",  "desc": "Temp uniformity across wafer"},
    "cure_oxygen_level":          {"min": 0.2, "max": 0.8, "unit": "%",   "desc": "Residual oxygen in chamber"},
    "inspect_defect_count":       {"min": 0,   "max": 0,   "unit": "",    "desc": "Visual defect count"},
    "inspect_visual_score":       {"min": 90,  "max": 100, "unit": "%",   "desc": "Visual inspection score"},
    "inspect_electrical_test":    {"min": 1,   "max": 1,   "unit": "",    "desc": "Electrical continuity pass/fail"},
    "inspect_reliability_score":  {"min": 92,  "max": 100, "unit": "%",   "desc": "Overall reliability score"},
    "inspect_dimensional_accuracy":{"min": 0,  "max": 20,  "unit": "μm",  "desc": "Dimensional offset"},
    "inspect_lead_coplanarity":   {"min": 30,  "max": 50,  "unit": "μm",  "desc": "Lead coplanarity"},
}

STAGE_PARAMS: Dict[str, List[str]] = {
    "die_attach":    [k for k in PARAM_META if k.startswith("die_")],
    "wire_bonding":  [k for k in PARAM_META if k.startswith("wire_")],
    "molding":       [k for k in PARAM_META if k.startswith("mold_")],
    "curing":        [k for k in PARAM_META if k.startswith("cure_")],
    "inspection":    [k for k in PARAM_META if k.startswith("inspect_")],
}

STAGE_DESCRIPTIONS = {
    "die_attach":   "Die attachment to substrate using epoxy",
    "wire_bonding": "Wire connections between die pads and package leads",
    "molding":      "Encapsulation with transfer-molded compound",
    "curing":       "Thermal curing of the molding compound",
    "inspection":   "Final visual, electrical, and dimensional quality inspection",
}

STAGE_COMMON_ISSUES = {
    "die_attach":   ["epoxy voids", "die misalignment", "temperature overshoot"],
    "wire_bonding": ["weak bonds", "wire breaks", "loop height collapse"],
    "molding":      ["void inclusions", "incomplete fill", "wire sweep"],
    "curing":       ["incomplete cure", "thermal non-uniformity", "moisture ingress"],
    "inspection":   ["electrical failures", "visual surface defects", "dimensional drift"],
}

# --------------------------------------------------------------------------- #
# Scenario profiles — full domain knowledge per failure mode
# Each "conditions" entry is (param, op, threshold) and is evaluated against live data.
# Multiple conditions are OR-ed to detect partial matches; score = matches/total.
# --------------------------------------------------------------------------- #
SCENARIO_PROFILES: Dict[str, Dict] = {
    "normal": {
        "name": "Normal Operation",
        "conditions": [],
        "affected_stages": [],
        "cascade_risks": [],
        "decision": "✅ CONTINUE",
        "root_cause": "All process parameters within normal operating range. No intervention required.",
        "immediate_actions": [
            "Continue normal production schedule",
            "Maintain regular SPC monitoring cadence (every 20–25 units)",
        ],
        "corrective_actions": [
            "No corrective action needed",
            "Consider minor fine-tuning if any parameter drifts within 10% of warning boundary",
        ],
        "spc_action": "Normal monitoring — no action required",
        "ml_expected": "GOOD",
    },
    "die_attach_drift": {
        "name": "Die Attach Temperature Drift",
        "conditions": [
            ("die_temperature", ">", 192),
            ("die_temperature", "<", 178),
            ("die_void_percentage", ">", 3.0),
        ],
        "affected_stages": ["die_attach"],
        "cascade_risks": [
            "Voids >5% will cascade → inspect_reliability_score drops ≥15 points",
            "Placement error >15 μm cascades → wire bonding force mis-tuned",
        ],
        "decision": "⚠️ ADJUST",
        "root_cause": (
            "Die attach oven temperature controller drift or thermocouple degradation. "
            "Gradual temperature rise drives epoxy outgassing → void formation. "
            "Root cause: oven PID drift, thermocouple ageing, or incorrect epoxy batch."
        ),
        "immediate_actions": [
            "Verify die attach oven temperature with external calibrated thermocouple",
            "Inspect thermocouple sensor for drift or mechanical damage",
            "Sample 3 units under X-ray for void percentage confirmation",
            "Review epoxy dispense volume and pot-life timer",
        ],
        "corrective_actions": [
            "Recalibrate oven PID controller — target 180–190 °C (±2 °C)",
            "Replace thermocouple if measured deviation > 3 °C from setpoint",
            "Reduce epoxy dispense volume by 5% if voids > 3%",
            "Check epoxy batch date code — discard if > 6 months old",
            "Run 5 qualification units before resuming full production",
        ],
        "spc_action": "Trigger SPC out-of-control signal. Quarantine last 10 units pending X-ray.",
        "ml_expected": "WARNING → SEVERE",
    },
    "wire_bonding_failure": {
        "name": "Wire Bonding Failure",
        "conditions": [
            ("wire_pull_strength", "<", 6.0),
            ("wire_bonding_force", "<", 35.0),
            ("wire_bonding_force", ">", 55.0),
            ("wire_ultrasonic_power", "<", 70.0),
            ("wire_ultrasonic_power", ">", 110.0),
        ],
        "affected_stages": ["wire_bonding"],
        "cascade_risks": [
            "Weak bonds (pull <6 gf) → direct inspection failure (electrical test FAIL)",
            "Low loop height (<200 μm) → mold temperature drops → wire sweep risk",
        ],
        "decision": "🛑 STOP BATCH",
        "root_cause": (
            "Wire bonding machine capillary wear, incorrect force/power settings, or "
            "substrate pad contamination. Weak bonds result from insufficient metal-to-metal "
            "diffusion at the bond interface. Pull strength <6 gf indicates imminent open-circuit risk."
        ),
        "immediate_actions": [
            "STOP production — perform 100% wire pull test on current units",
            "Inspect bonding capillary under 100× microscope for wear, plugging, or contamination",
            "Verify ultrasonic power amplitude with calibrated power meter",
            "Check substrate pad surface for oxidation, contamination, or intermetallic growth",
        ],
        "corrective_actions": [
            "Replace capillary (typical lifespan: 30,000–50,000 bonds)",
            "Recalibrate bond force to 40–52 gf using bond tester load cell",
            "Adjust ultrasonic power to 85–100 mW",
            "Clean substrate pads with IPA wipe; bake at 120 °C for 30 min to remove moisture",
            "Run 10 bond optimization coupons before restarting production",
        ],
        "spc_action": "CRITICAL HOLD — Do not ship. Escalate to process engineer. Review last 50 bonded units.",
        "ml_expected": "SEVERE",
    },
    "molding_issue": {
        "name": "Molding Compound Issue",
        "conditions": [
            ("mold_voids", ">", 1.5),
            ("mold_compound_viscosity", ">", 155.0),
            ("mold_compound_viscosity", "<", 80.0),
            ("mold_fill_time", ">", 6.0),
        ],
        "affected_stages": ["molding"],
        "cascade_risks": [
            "Mold voids >2% → cure uniformity degrades (+1.5°C non-uniformity)",
            "Incomplete fill → visual defects at inspection",
        ],
        "decision": "⚠️ ADJUST",
        "root_cause": (
            "Mold compound batch variability (viscosity out-of-spec), incorrect transfer "
            "pressure/speed, or contaminated mold cavity causing void inclusions or incomplete fill. "
            "High viscosity (>155 Pa·s) indicates compound age or cold storage issue."
        ),
        "immediate_actions": [
            "Check mold compound batch certificate (viscosity spec: 115–140 Pa·s)",
            "Inspect mold cavity for contamination, residue buildup, or runner blockage",
            "Review transfer pressure and plunger speed settings",
            "Perform short-shot test (50% fill) to observe fill pattern and void locations",
        ],
        "corrective_actions": [
            "Replace mold compound if viscosity outside 80–155 Pa·s acceptance range",
            "Clean mold cavity with mold-release agent and lint-free wipe",
            "Adjust transfer speed to 11–14 mm/s; verify plunger position sensor",
            "Increase mold temperature by 2–3°C to reduce compound viscosity",
            "Apply vacuum assist molding if voids persist after pressure/speed adjustment",
        ],
        "spc_action": "Quarantine affected batch. Sample 10% for X-ray void inspection before shipment.",
        "ml_expected": "WARNING → SEVERE",
    },
    "curing_incomplete": {
        "name": "Incomplete Curing",
        "conditions": [
            ("cure_time", "<", 120.0),
            ("cure_temperature", "<", 178.0),
            ("cure_uniformity", ">", 2.5),
        ],
        "affected_stages": ["curing"],
        "cascade_risks": [
            "Under-cure → inspect_reliability_score drops (cure_time <120 min → -10 pts)",
            "Under-cure → long-term field delamination, moisture absorption, popcorn cracking",
        ],
        "decision": "🛑 STOP BATCH",
        "root_cause": (
            "Cure oven malfunction — insufficient temperature or cure time. "
            "Root causes: oven heater element failure, door seal degradation allowing heat loss, "
            "incorrect recipe loaded, or thermocouple failure showing false 'at temperature' reading."
        ),
        "immediate_actions": [
            "Stop oven immediately — verify temperature with calibrated Pt100 reference probe",
            "Inspect oven door seals for gaps, wear, or deformation",
            "Check cure profile recipe — confirm correct time (140–165 min) and temperature (178–184°C)",
            "Measure thermal uniformity: ±2°C max across all rack positions",
        ],
        "corrective_actions": [
            "Re-cure incomplete batch at 180°C for 150 min if gel time not exceeded",
            "Recalibrate oven controller — verify setpoint vs. actual temperature",
            "Replace door seals if temperature drop at door > 3°C",
            "Reposition units to center rack zone if uniformity > 2.5°C",
            "Perform DMA (Dynamic Mechanical Analysis) on 3 samples to verify Tg after re-cure",
        ],
        "spc_action": "HOLD all units from this cure lot. Mandatory reliability re-test before release.",
        "ml_expected": "SEVERE",
    },
    "inspection_failure": {
        "name": "Inspection Failure",
        "conditions": [
            ("inspect_defect_count", ">=", 3.0),
            ("inspect_electrical_test", "==", 0.0),
            ("inspect_reliability_score", "<", 85.0),
            ("inspect_visual_score", "<", 85.0),
        ],
        "affected_stages": ["inspection"],
        "cascade_risks": [
            "Electrical test failure → direct batch rejection, no rework possible",
            "Multiple defects → traceability review required for all units in batch",
        ],
        "decision": "🛑 EMERGENCY STOP",
        "root_cause": (
            "Multiple upstream process failures (die attach voids, weak bonds, or mold defects) "
            "propagating to final inspection, OR systematic contamination in cleanroom. "
            "Electrical failure combined with visual defects indicates multi-stage breakdown."
        ),
        "immediate_actions": [
            "HALT PRODUCTION — quarantine entire batch immediately",
            "Do not ship any units from this batch",
            "Notify quality manager and document defect types with photos",
            "Preserve all process logs (oven profiles, bond charts, mold records) for analysis",
        ],
        "corrective_actions": [
            "100% inspection of all units in current and previous batch",
            "Failure analysis: cross-section 3 failed units to identify defect origin",
            "5-Why root cause analysis — trace back through die attach → wire bond → mold",
            "Implement corrective action at root stage before restarting",
            "Customer notification required if any units in transit",
        ],
        "spc_action": "CRITICAL STOP — Quality hold on entire batch. Do not ship. Customer notification mandatory.",
        "ml_expected": "SEVERE",
    },
    "cascading_failure": {
        "name": "Cascading Multi-Stage Failure",
        "conditions": [
            ("die_void_percentage", ">", 5.0),
            ("wire_pull_strength", "<", 6.0),
            ("inspect_reliability_score", "<", 85.0),
            ("inspect_defect_count", ">=", 3.0),
        ],
        "affected_stages": ["die_attach", "wire_bonding", "inspection"],
        "cascade_risks": [
            "Die voids → reduced bonding area → weak bonds → electrical failure",
            "Multiple stage failures indicate common root cause (material or environment)",
        ],
        "decision": "🛑 EMERGENCY STOP",
        "root_cause": (
            "Systemic failure originating in die attach (high voids) cascading through wire bonding "
            "(reduced bond area on voided die pad) to inspection failure. "
            "Possible common root cause: substrate contamination, epoxy outgassing, or cleanroom particulate event."
        ),
        "immediate_actions": [
            "EMERGENCY STOP — halt entire production line immediately",
            "Do not process any in-queue units — quarantine all in-progress work",
            "Alert process engineer and quality manager immediately (escalation required)",
            "Preserve all tooling, materials, and environment logs for failure analysis",
        ],
        "corrective_actions": [
            "Material traceability review: audit substrate lot, epoxy batch, wire spool",
            "Environmental audit: check cleanroom particle count, temperature, and humidity",
            "Full equipment calibration audit: die bonder, wire bonder, and cure oven",
            "Systematic 5-Why analysis across all three affected stages before restart",
            "Run 20-unit qualification build before resuming production",
        ],
        "spc_action": "EMERGENCY SHUTDOWN — Production stop mandatory. Quality hold on all units. Executive notification.",
        "ml_expected": "SEVERE (multi-stage)",
    },
    "intermittent_warning": {
        "name": "Intermittent Process Warning",
        "conditions": [
            ("wire_bonding_force", "<", 40.0),
            ("wire_bonding_force", ">", 52.0),
            ("wire_ultrasonic_power", "<", 85.0),
            ("wire_ultrasonic_power", ">", 100.0),
            ("die_temperature", ">", 190.0),
        ],
        "affected_stages": ["wire_bonding"],
        "cascade_risks": [
            "Sustained warning over 10–20 cycles may escalate to wire bonding failure",
        ],
        "decision": "⚠️ MONITOR",
        "root_cause": (
            "Gradual equipment drift or process instability — typical causes: capillary wear "
            "(early stage), substrate batch-to-batch variation, or environmental factors "
            "(temperature/humidity changes in bonding area). Not yet critical but trending toward threshold."
        ),
        "immediate_actions": [
            "Increase monitoring frequency to every 5 units",
            "Enable SPC control charts for wire bonding parameters",
            "Sample 5 units for destructive wire pull test to validate actual bond strength",
            "Check bonding area environment (temperature, humidity, particle count)",
        ],
        "corrective_actions": [
            "Schedule capillary replacement at next maintenance window",
            "Tighten wire bonding process window by 10% as precaution",
            "Verify substrate batch consistency with supplier CoC",
            "Confirm environmental controls: 22±1°C, <50% RH in wire bonding area",
        ],
        "spc_action": "Add to SPC monitoring queue. Review at next shift change. Trend chart mandatory.",
        "ml_expected": "WARNING",
    },
}


def _evaluate_scenario_conditions(data: Dict, conditions: List) -> float:
    """
    Evaluate how many scenario signature conditions are met.
    Returns match ratio [0.0, 1.0].
    """
    if not conditions:
        return 0.0
    matched = 0
    for param, op, threshold in conditions:
        val = data.get(param)
        if val is None:
            continue
        try:
            val = float(val)
            if op == ">"  and val >  threshold: matched += 1
            elif op == "<"  and val <  threshold: matched += 1
            elif op == ">=" and val >= threshold: matched += 1
            elif op == "<=" and val <= threshold: matched += 1
            elif op == "==" and val == threshold: matched += 1
        except (TypeError, ValueError):
            continue
    return matched / len(conditions)


class CopilotService:
    """
    Enhanced AI Copilot service with health scoring, trend analysis,
    forecasting, and richer natural-language responses.
    """

    def __init__(self):
        self.ml_service = get_ml_service()
        # In-session history buffer for trend analysis
        self._history: List[Dict] = []

    # ---------------------------------------------------------------------- #
    # Public API
    # ---------------------------------------------------------------------- #

    def process_query(self, query: str, context: Optional[Dict] = None) -> Dict:
        """Route a natural-language query to the right handler."""
        q = query.lower()

        # Consolidated decision handler — highest priority
        if any(w in q for w in ["decision", "assess", "evaluate", "diagnose",
                                  "what should i", "what to do", "give me a decision",
                                  "full report", "complete assessment", "status report"]):
            return self._handle_decision_query(query, context)
        if any(w in q for w in ["health", "score", "stage score", "how healthy"]):
            return self._handle_health_query(query, context)
        if any(w in q for w in ["forecast", "predict future", "will it", "trend", "drift"]):
            return self._handle_forecast_query(query, context)
        if any(w in q for w in ["why", "reason", "cause", "root cause",
                                  "alert", "critical", "severe", "urgent"]):
            return self._handle_why_query(query, context)
        if any(w in q for w in ["analyze", "analysis", "check", "inspect"]):
            return self._handle_analysis_query(query, context)
        if any(w in q for w in ["recommend", "suggest", "optimize", "improve", "fix"]):
            return self._handle_recommendation_query(query, context)
        if any(w in q for w in ["what", "explain", "tell", "describe", "how does"]):
            return self._handle_explanation_query(query, context)
        if any(w in q for w in ["compare", "difference", "versus", "vs"]):
            return self._handle_comparison_query(query, context)
        if any(w in q for w in ["scenario", "mode", "failure mode"]):
            return self._handle_decision_query(query, context)

        return self._handle_general_query(query, context)

    def _detect_scenario(self, data: Dict) -> Tuple[str, Dict, float]:
        """
        Identify the most likely active failure scenario from live parameter data.

        Strategy:
          1. Cascading failure takes priority — it has the most conditions matched.
          2. For the rest, pick the scenario with the highest condition match ratio.
          3. Fall back to 'normal' if no scenario scores above 0.

        Returns:
            (scenario_key, scenario_profile, confidence)
        """
        scores: Dict[str, float] = {}
        for key, profile in SCENARIO_PROFILES.items():
            if key == "normal":
                continue
            score = _evaluate_scenario_conditions(data, profile["conditions"])
            if score > 0:
                scores[key] = score

        if not scores:
            return "normal", SCENARIO_PROFILES["normal"], 0.95

        # Cascading failure: override if both die_void AND wire_pull AND reliability all fail
        cascade_conds = [c for c in SCENARIO_PROFILES["cascading_failure"]["conditions"]]
        cascade_score = _evaluate_scenario_conditions(data, cascade_conds)
        if cascade_score >= 0.5:
            scores["cascading_failure"] = cascade_score + 0.2  # boost priority

        best = max(scores, key=lambda k: scores[k])
        conf = min(0.50 + scores[best] * 0.48, 0.98)
        return best, SCENARIO_PROFILES[best], round(conf, 2)

    def add_to_history(self, data: Dict):
        """Append a process data point to the session trend buffer (max 50)."""
        self._history.append(data)
        if len(self._history) > 50:
            self._history.pop(0)

    def get_process_health(self, data: Dict) -> Dict:
        """Return per-stage and overall health scores (0–100)."""
        stage_scores = {}
        for stage, params in STAGE_PARAMS.items():
            scores = []
            for p in params:
                if p not in data:
                    continue
                val = data[p]
                lo = PARAM_META[p]["min"]
                hi = PARAM_META[p]["max"]
                if lo == hi:  # binary (0/1)
                    scores.append(100.0 if val == hi else 0.0)
                elif lo <= val <= hi:
                    scores.append(100.0)
                else:
                    spread = (hi - lo) if hi != lo else 1.0
                    dev = min(abs(val - lo), abs(val - hi))
                    scores.append(max(0.0, 100.0 - (dev / spread * 100)))
            stage_scores[stage] = round(sum(scores) / len(scores), 1) if scores else 100.0

        overall = round(sum(stage_scores.values()) / len(stage_scores), 1)
        return {"stages": stage_scores, "overall": overall}

    # ---------------------------------------------------------------------- #
    # Query handlers
    # ---------------------------------------------------------------------- #

    def _handle_health_query(self, query: str, context: Optional[Dict]) -> Dict:
        if not context or "current_data" not in context:
            return self._no_data_response("health")

        data = context["current_data"]
        health = self.get_process_health(data)
        stages = health["stages"]
        overall = health["overall"]

        emoji = {r: ("🟢" if s >= 90 else "🟡" if s >= 70 else "🔴")
                 for r, s in stages.items()}

        answer = f"## Process Health Report\n\n"
        answer += f"**Overall Health Score: {overall:.0f} / 100**\n\n"
        answer += "| Stage | Score | Status |\n|-------|-------|--------|\n"
        for stage, score in stages.items():
            label = "Healthy" if score >= 90 else "Caution" if score >= 70 else "Critical"
            answer += f"| {stage.replace('_', ' ').title()} | {score:.0f} | {emoji[stage]} {label} |\n"

        worst = min(stages, key=lambda s: stages[s])
        if stages[worst] < 90:
            answer += f"\n**Priority focus:** {worst.replace('_', ' ').title()} stage "
            answer += f"(score {stages[worst]:.0f}) — check "
            answer += ", ".join(STAGE_COMMON_ISSUES[worst][:2]) + "."

        return {
            "type": "health",
            "answer": answer,
            "confidence": 0.95,
            "health_scores": health,
            "actions": ["review_worst_stage"],
        }

    def _handle_forecast_query(self, query: str, context: Optional[Dict]) -> Dict:
        if not context or "current_data" not in context:
            return self._no_data_response("forecast")

        data = context["current_data"]
        history = context.get("history", self._history)

        trending = []
        if len(history) >= 3:
            recent = history[-5:]
            for param, meta in PARAM_META.items():
                vals = [h.get(param) for h in recent if h.get(param) is not None]
                if len(vals) < 3:
                    continue
                # Linear slope (simple)
                n = len(vals)
                xs = list(range(n))
                x_mean = sum(xs) / n
                y_mean = sum(vals) / n
                num = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, vals))
                den = sum((x - x_mean) ** 2 for x in xs) or 1
                slope = num / den
                lo, hi = meta["min"], meta["max"]
                # Extrapolate 5 cycles
                projected = vals[-1] + slope * 5
                if projected < lo or projected > hi:
                    direction = "rising" if slope > 0 else "falling"
                    trending.append({
                        "param": param,
                        "current": vals[-1],
                        "slope": slope,
                        "projected": projected,
                        "direction": direction,
                        "unit": meta["unit"],
                    })

        if trending:
            answer = f"## Trend Forecast (next ~5 cycles)\n\n"
            answer += f"**{len(trending)} parameter(s) trending toward out-of-range:**\n\n"
            for t in trending[:5]:
                status = "⚠️ WARNING" if abs(t["slope"]) < 0.5 else "🚨 ALERT"
                answer += (
                    f"- **{t['param']}** {status}: currently {t['current']:.2f}{t['unit']}, "
                    f"{t['direction']} at {abs(t['slope']):.3f}/cycle → "
                    f"projected **{t['projected']:.2f}{t['unit']}**\n"
                )
            answer += "\n**Recommended action:** Intervene before the next 5 cycles to prevent escalation."
        else:
            current_health = self.get_process_health(data)["overall"]
            answer = (
                f"## Trend Forecast\n\n"
                f"No concerning trends detected in the available history.\n\n"
                f"Current overall health: **{current_health:.0f}/100**. "
                f"Process appears stable. Continue monitoring every 3–5 cycles."
            )

        return {
            "type": "forecast",
            "answer": answer,
            "confidence": 0.80,
            "trending_params": trending,
            "actions": ["monitor_trends"],
        }

    def _handle_why_query(self, query: str, context: Optional[Dict]) -> Dict:
        if not context or "current_data" not in context:
            return self._no_data_response("why")

        data = context["current_data"]
        status = data.get("predicted_status", data.get("status", "UNKNOWN"))
        abnormal = self._identify_abnormal_parameters(data)

        # Scenario detection
        scenario_key, scenario_profile, scenario_conf = self._detect_scenario(data)

        if self.ml_service.is_loaded():
            explanation = self.ml_service.explain_prediction(data, top_n=5)
            top_features = explanation.get("top_contributors", [])
        else:
            top_features = []

        if status == "SEVERE":
            answer = f"## 🔴 Root Cause Analysis — SEVERE\n\n"

            # Scenario identification block
            if scenario_key != "normal":
                answer += (
                    f"### Detected Failure Mode: **{scenario_profile['name']}**  "
                    f"*(confidence {scenario_conf:.0%})*\n\n"
                    f"**Affected Stages:** {', '.join(s.replace('_', ' ').title() for s in scenario_profile['affected_stages'])}\n\n"
                    f"**Root Cause:** {scenario_profile['root_cause']}\n\n"
                )

            answer += "**Critical Parameters:**\n\n"
            for param, info in abnormal[:4]:
                arrow = "↑" if info["value"] > info["normal_max"] else "↓"
                answer += (
                    f"- **{param}** {arrow} `{info['value']:.2f} {info['unit']}`  "
                    f"*(normal: {info['normal_min']}–{info['normal_max']} {info['unit']})*\n"
                    f"  → {info['impact']}\n"
                )

            if top_features:
                answer += "\n**ML Feature Drivers:**\n"
                for f in top_features[:3]:
                    answer += f"  - {f['feature']}: {f['importance']:.1%} importance\n"

            cross = self._analyze_cross_stage_impact(data, abnormal)
            if cross:
                answer += f"\n**Cross-Stage Cascade Risk:**\n{cross}"

            if scenario_key != "normal" and scenario_profile.get("cascade_risks"):
                answer += "\n**Scenario Cascade Risks:**\n"
                for risk in scenario_profile["cascade_risks"]:
                    answer += f"  - {risk}\n"

            answer += f"\n**Recommended Decision:** {scenario_profile.get('decision', '⚠️ ADJUST')}"
            conf = 0.92

        elif status == "WARNING":
            answer = f"## ⚠️ Status Analysis — WARNING\n\n"

            if scenario_key != "normal":
                answer += (
                    f"**Likely Scenario:** {scenario_profile['name']} *(conf {scenario_conf:.0%})*\n\n"
                    f"**Root Cause:** {scenario_profile['root_cause']}\n\n"
                )

            answer += "**Parameters outside normal range (monitor closely):**\n\n"
            for param, info in abnormal[:3]:
                arrow = "↑" if info["value"] > info["normal_max"] else "↓"
                answer += f"- **{param}** {arrow} `{info['value']:.2f} {info['unit']}` (range: {info['normal_min']}–{info['normal_max']})\n"
            answer += "\n*Escalation to SEVERE is likely if not corrected within 5–10 cycles.*"
            conf = 0.82

        else:
            answer = (
                "## ✅ Status Analysis — GOOD\n\n"
                "All parameters are within normal operating ranges.\n"
                "No immediate action required. Continue scheduled monitoring."
            )
            conf = 0.97

        return {
            "type": "why",
            "answer": answer,
            "confidence": conf,
            "abnormal_parameters": abnormal,
            "top_features": top_features,
            "detected_scenario": scenario_key,
            "actions": ["review_parameters"],
        }

    def _handle_analysis_query(self, query: str, context: Optional[Dict]) -> Dict:
        q = query.lower()
        stage_map = {
            "die_attach":   ["die attach", "die"],
            "wire_bonding": ["wire bond", "wire", "bonding"],
            "molding":      ["mold"],
            "curing":       ["cur"],
            "inspection":   ["inspect"],
        }
        stage = "all"
        for s, keywords in stage_map.items():
            if any(kw in q for kw in keywords):
                stage = s
                break

        if not context or "current_data" not in context:
            return self._no_data_response("analysis")

        data = context["current_data"]
        return self._analyze_specific_stage(data, stage) if stage != "all" else self._analyze_all_stages(data)

    def _handle_recommendation_query(self, query: str, context: Optional[Dict]) -> Dict:
        if not context or "current_data" not in context:
            return self._no_data_response("recommendation")

        data = context["current_data"]
        status = data.get("predicted_status", data.get("status", "UNKNOWN"))
        abnormal = self._identify_abnormal_parameters(data)

        # Detect active scenario for specific advice
        scenario_key, scenario_profile, scenario_conf = self._detect_scenario(data)

        if not abnormal and scenario_key == "normal":
            return {
                "type": "recommendation",
                "answer": (
                    "## Optimization Recommendations\n\n"
                    "**Process is operating normally.** No adjustments needed.\n\n"
                    "Continue monitoring for parameter drift. Run a forecast analysis "
                    "to see if any parameters are trending toward threshold."
                ),
                "confidence": 0.92,
                "actions": ["continue_monitoring"],
            }

        answer = f"## 🔧 Optimization Recommendations ({status})\n\n"

        # Scenario-specific block first if a scenario is detected
        if scenario_key != "normal":
            answer += (
                f"### Detected: **{scenario_profile['name']}**  *(conf {scenario_conf:.0%})*\n\n"
                f"**Decision: {scenario_profile['decision']}**\n\n"
            )
            if scenario_profile.get("immediate_actions"):
                answer += "#### ⚡ Immediate Actions (do now)\n"
                for i, action in enumerate(scenario_profile["immediate_actions"], 1):
                    answer += f"{i}. {action}\n"
                answer += "\n"
            if scenario_profile.get("corrective_actions"):
                answer += "#### 🔨 Corrective Actions (root-cause fix)\n"
                for i, action in enumerate(scenario_profile["corrective_actions"], 1):
                    answer += f"{i}. {action}\n"
                answer += "\n"
            answer += f"**SPC/Quality Action:** {scenario_profile.get('spc_action', 'Monitor closely')}\n\n"
            answer += "---\n\n"

        # Parameter-level recommendations
        recommendations = [self._generate_recommendation(p, i) for p, i in abnormal[:5]]
        recommendations = [r for r in recommendations if r]
        if recommendations:
            answer += "#### 📊 Parameter-Level Adjustments\n\n"
            for idx, rec in enumerate(recommendations, 1):
                badge = "🔴 CRITICAL" if rec["priority"] == "CRITICAL" else "🟡 MEDIUM"
                answer += (
                    f"**{idx}. {rec['parameter']}** {badge}\n"
                    f"- Current: `{rec['current']:.2f} {rec['unit']}`\n"
                    f"- Target: `{rec['target_min']:.1f}–{rec['target_max']:.1f} {rec['unit']}`\n"
                    f"- Action: {rec['action']}\n\n"
                )

        answer += (
            "**Implementation Order:**\n"
            "1. Address CRITICAL items first\n"
            "2. Monitor 5–10 cycles after each adjustment\n"
            "3. Verify improvement before the next change\n"
        )

        return {
            "type": "recommendation",
            "answer": answer,
            "confidence": 0.87,
            "recommendations": recommendations,
            "detected_scenario": scenario_key,
            "actions": ["implement_recommendations"],
        }

    def _handle_explanation_query(self, query: str, context: Optional[Dict]) -> Dict:
        q = query.lower()
        for stage, desc in STAGE_DESCRIPTIONS.items():
            if stage.replace("_", " ") in q or stage.split("_")[0] in q:
                params = STAGE_PARAMS[stage]
                answer = f"## {stage.replace('_', ' ').title()} Stage\n\n"
                answer += f"{desc}\n\n"
                answer += "**Critical Parameters:**\n"
                for p in params[:5]:
                    m = PARAM_META.get(p, {})
                    answer += f"- **{p}**: {m.get('min', '?')}–{m.get('max', '?')} {m.get('unit', '')} — {m.get('desc', '')}\n"
                answer += "\n**Common Issues:**\n"
                for issue in STAGE_COMMON_ISSUES[stage]:
                    answer += f"- {issue}\n"
                return {"type": "explanation", "answer": answer, "confidence": 1.0, "actions": []}

        return {
            "type": "explanation",
            "answer": (
                "## Packaging Process Overview\n\n"
                "This system monitors **5 sequential stages**:\n\n"
                "1. **Die Attach** — bonding the semiconductor die to the substrate\n"
                "2. **Wire Bonding** — connecting die pads to package leads via gold/copper wires\n"
                "3. **Molding** — encapsulating the assembly in protective resin\n"
                "4. **Curing** — thermally curing the mold compound\n"
                "5. **Inspection** — visual, electrical, and dimensional QC\n\n"
                "Ask me about any specific stage for detailed parameter ranges and common failure modes."
            ),
            "confidence": 1.0,
            "actions": [],
        }

    def _handle_comparison_query(self, query: str, context: Optional[Dict]) -> Dict:
        if not context or "current_data" not in context:
            return self._no_data_response("comparison")

        data = context["current_data"]
        health = self.get_process_health(data)
        stages = health["stages"]
        best = max(stages, key=lambda s: stages[s])
        worst = min(stages, key=lambda s: stages[s])

        answer = (
            f"## Stage-to-Stage Comparison\n\n"
            f"**Best stage:** {best.replace('_', ' ').title()} ({stages[best]:.0f}/100)\n"
            f"**Worst stage:** {worst.replace('_', ' ').title()} ({stages[worst]:.0f}/100)\n\n"
            f"**Gap:** {stages[best] - stages[worst]:.0f} points — "
        )
        if stages[best] - stages[worst] > 20:
            answer += "significant disparity; focus resources on the lowest stage."
        else:
            answer += "relatively balanced process across all stages."

        return {"type": "comparison", "answer": answer, "confidence": 0.88, "actions": []}

    def _handle_decision_query(self, query: str, context: Optional[Dict]) -> Dict:
        """
        Consolidated AI Decision Assistant — master handler.
        Aggregates: ML status, scenario detection, health scores, abnormal params,
        cascade risks, and ranked action plan into one authoritative response.
        """
        if not context or "current_data" not in context:
            return self._no_data_response("decision")

        data = context["current_data"]
        status = data.get("predicted_status", data.get("status", "UNKNOWN"))
        confidence = data.get("confidence", 0.0)
        batch_id = data.get("batch_id", "N/A")

        # Gather all intelligence
        health = self.get_process_health(data)
        abnormal = self._identify_abnormal_parameters(data)
        scenario_key, scenario_profile, scenario_conf = self._detect_scenario(data)

        if self.ml_service.is_loaded():
            explanation = self.ml_service.explain_prediction(data, top_n=3)
            top_features = explanation.get("top_contributors", [])
        else:
            top_features = []

        # Status icon
        status_icon = {"GOOD": "✅", "WARNING": "⚠️", "SEVERE": "🔴"}.get(status, "❓")
        decision = scenario_profile.get("decision", "⚠️ MONITOR")

        # Build comprehensive response
        answer = f"# 🤖 AI Decision Report — Batch {batch_id}\n\n"
        answer += f"---\n\n"

        # --- EXECUTIVE SUMMARY ---
        answer += f"## Executive Summary\n\n"
        answer += f"| Item | Value |\n|------|-------|\n"
        answer += f"| ML Status | {status_icon} **{status}** (conf {confidence:.0%}) |\n"
        answer += f"| Overall Health | **{health['overall']:.0f}/100** |\n"
        answer += f"| Detected Scenario | **{scenario_profile['name']}** (conf {scenario_conf:.0%}) |\n"
        answer += f"| Recommended Decision | {decision} |\n\n"

        # --- STAGE HEALTH ---
        answer += "## Stage Health Scores\n\n"
        answer += "| Stage | Score | Status |\n|-------|-------|--------|\n"
        for stage, score in health["stages"].items():
            icon = "✅" if score >= 90 else "⚠️" if score >= 70 else "🔴"
            label = "Healthy" if score >= 90 else "Caution" if score >= 70 else "Critical"
            answer += f"| {stage.replace('_', ' ').title()} | {score:.0f}/100 | {icon} {label} |\n"
        answer += "\n"

        # --- SCENARIO DIAGNOSIS ---
        if scenario_key != "normal":
            answer += f"## Failure Mode Diagnosis\n\n"
            answer += f"**Scenario:** {scenario_profile['name']}\n\n"
            answer += f"**Root Cause:** {scenario_profile['root_cause']}\n\n"
            if scenario_profile.get("cascade_risks"):
                answer += "**Cascade Risks:**\n"
                for risk in scenario_profile["cascade_risks"]:
                    answer += f"  - {risk}\n"
                answer += "\n"

        # --- CRITICAL PARAMETERS ---
        if abnormal:
            answer += "## Critical Parameters\n\n"
            for param, info in abnormal[:5]:
                arrow = "↑" if info["value"] > info["normal_max"] else "↓"
                badge = "🔴" if info["severity"] == "SEVERE" else "🟡"
                answer += (
                    f"- {badge} **{param}** {arrow} `{info['value']:.2f} {info['unit']}` "
                    f"*(normal: {info['normal_min']}–{info['normal_max']} {info['unit']})*\n"
                )
            answer += "\n"

        # --- ML TOP FEATURES ---
        if top_features:
            answer += "## ML Decision Drivers\n\n"
            for f in top_features[:3]:
                answer += f"- **{f['feature']}**: {f['importance']:.1%} influence on classification\n"
            answer += "\n"

        # --- ACTION PLAN ---
        answer += "## Action Plan\n\n"
        if scenario_key != "normal":
            if scenario_profile.get("immediate_actions"):
                answer += "### ⚡ Do Now\n"
                for i, action in enumerate(scenario_profile["immediate_actions"][:3], 1):
                    answer += f"{i}. {action}\n"
                answer += "\n"
            if scenario_profile.get("corrective_actions"):
                answer += "### 🔨 Root-Cause Fix\n"
                for i, action in enumerate(scenario_profile["corrective_actions"][:3], 1):
                    answer += f"{i}. {action}\n"
                answer += "\n"
            answer += f"### 📋 Quality/SPC Action\n{scenario_profile.get('spc_action', 'Monitor closely')}\n"
        else:
            answer += "✅ Process is healthy. Maintain normal monitoring cadence.\n"

        # --- WATSONX.AI ENRICHMENT (optional) ---
        wx_prompt = (
            f"Semiconductor packaging process status:\n"
            f"ML Status: {status} (confidence {confidence:.0%})\n"
            f"Scenario: {scenario_profile['name']}\n"
            f"Health: {health['overall']:.0f}/100\n"
            f"Abnormal parameters: {[p for p, _ in abnormal[:3]]}\n"
            f"Root cause: {scenario_profile['root_cause']}\n"
            f"Provide a 2-sentence engineering recommendation for this situation.\n###"
        )
        wx_text = _watsonx_generate(wx_prompt, max_tokens=150)
        if wx_text:
            answer += f"\n### 🧠 IBM Granite Engineering Insight\n{wx_text}\n"

        return {
            "type": "decision",
            "answer": answer,
            "confidence": max(confidence, scenario_conf),
            "health_scores": health,
            "detected_scenario": scenario_key,
            "abnormal_parameters": abnormal,
            "top_features": top_features,
            "decision": decision,
            "actions": ["implement_decision"],
        }

    def _handle_general_query(self, query: str, context: Optional[Dict]) -> Dict:
        health_snippet = ""
        if context and "current_data" in context:
            health = self.get_process_health(context["current_data"])
            health_snippet = f"\n\n*Current overall health: **{health['overall']:.0f}/100***"

        return {
            "type": "general",
            "answer": (
                "## IBM Bob AI Copilot\n\n"
                "I can assist you with:\n\n"
                "| Query Type | Example |\n"
                "|------------|----------|\n"
                "| 🤖 Full Decision Report | 'Give me a full assessment' |\n"
                "| 🔍 Root cause | 'Why is this batch severe?' |\n"
                "| 📊 Stage analysis | 'Analyze wire bonding' |\n"
                "| 💊 Health scores | 'Show process health' |\n"
                "| 📈 Trend forecast | 'Forecast next 5 cycles' |\n"
                "| 🔧 Recommendations | 'How can I optimize?' |\n"
                "| 📚 Explanations | 'Explain die attach' |\n"
                "| 🔄 Comparison | 'Compare stages' |\n"
                f"{health_snippet}"
            ),
            "confidence": 0.9,
            "actions": [],
        }

    # ---------------------------------------------------------------------- #
    # Internal helpers
    # ---------------------------------------------------------------------- #

    def _no_data_response(self, query_type: str) -> Dict:
        return {
            "type": query_type,
            "answer": (
                "I need current process data to answer that.\n\n"
                "**Generate data** using the sidebar, then ask me again."
            ),
            "confidence": 0.0,
            "actions": ["generate_data"],
        }

    def _identify_abnormal_parameters(self, data: Dict) -> List[Tuple[str, Dict]]:
        abnormal = []
        for param, meta in PARAM_META.items():
            if param not in data:
                continue
            val = data[param]
            lo, hi = meta["min"], meta["max"]
            if val < lo or val > hi:
                severity = "SEVERE" if (val < lo * 0.85 or val > hi * 1.15) else "WARNING"
                abnormal.append((param, {
                    "value": val,
                    "normal_min": lo,
                    "normal_max": hi,
                    "unit": meta["unit"],
                    "severity": severity,
                    "impact": meta["desc"],
                    "warning_threshold": hi * 0.95,
                    "severe_threshold": hi * 1.05,
                }))
        abnormal.sort(key=lambda x: (x[1]["severity"] == "SEVERE"), reverse=True)
        return abnormal

    def _analyze_cross_stage_impact(self, data: Dict, abnormal: List) -> str:
        impacts = []
        issue_params = {p for p, _ in abnormal}
        cross_deps = CROSS_STAGE_DEPENDENCIES if isinstance(CROSS_STAGE_DEPENDENCIES, list) else []
        for dep in cross_deps:
            if any(p in issue_params for p in dep.get("source_params", [])):
                impacts.append(f"- Issue may cascade to **{dep['target_stage']}** stage")
        return "\n".join(impacts[:3]) if impacts else ""

    def _analyze_all_stages(self, data: Dict) -> Dict:
        health = self.get_process_health(data)
        answer = "## Complete Process Analysis\n\n"
        for stage, score in health["stages"].items():
            icon = "✅" if score >= 90 else "⚠️" if score >= 70 else "🔴"
            answer += f"**{icon} {stage.replace('_', ' ').title()}** — Health: {score:.0f}/100\n"
            params = STAGE_PARAMS[stage]
            for p in params:
                if p not in data:
                    continue
                val = data[p]
                lo, hi = PARAM_META[p]["min"], PARAM_META[p]["max"]
                if not (lo <= val <= hi):
                    unit = PARAM_META[p]["unit"]
                    answer += f"  ⚠ `{p}` = {val:.2f}{unit} (range: {lo}–{hi})\n"
            answer += "\n"
        answer += f"**Overall Health: {health['overall']:.0f}/100**"
        return {"type": "analysis", "answer": answer, "confidence": 0.90, "actions": []}

    def _analyze_specific_stage(self, data: Dict, stage: str) -> Dict:
        if stage not in STAGE_PARAMS:
            return {"type": "analysis", "answer": f"Unknown stage: {stage}", "confidence": 0.0, "actions": []}

        params = STAGE_PARAMS[stage]
        health = self.get_process_health(data)
        stage_score = health["stages"].get(stage, 100)

        answer = f"## {stage.replace('_', ' ').title()} Stage Analysis\n\n"
        answer += f"{STAGE_DESCRIPTIONS[stage]}\n\n"
        answer += f"**Stage Health: {stage_score:.0f}/100**\n\n"
        answer += "**Parameter Status:**\n\n"
        answer += "| Parameter | Value | Normal Range | Status |\n|-----------|-------|--------------|--------|\n"
        for p in params:
            if p not in data:
                continue
            val = data[p]
            meta = PARAM_META[p]
            lo, hi = meta["min"], meta["max"]
            unit = meta["unit"]
            ok = lo <= val <= hi
            status_icon = "✅" if ok else "⚠️"
            answer += f"| {p} | {val:.2f} {unit} | {lo}–{hi} {unit} | {status_icon} |\n"

        return {"type": "analysis", "answer": answer, "confidence": 0.92, "actions": []}

    def _get_stage_status(self, data: Dict, critical_params: List[str]) -> Dict:
        issues = []
        for param in critical_params:
            if param not in data:
                continue
            val = data[param]
            meta = PARAM_META.get(param, {})
            lo, hi = meta.get("min", 0), meta.get("max", 100)
            if not (lo <= val <= hi):
                issues.append(f"{param} out of range ({val:.2f})")
        n = len(issues)
        return {
            "status": "✅ GOOD" if n == 0 else "⚠️ WARNING" if n == 1 else "🔴 SEVERE",
            "issues": issues,
        }

    def _generate_recommendation(self, param: str, info: Dict) -> Optional[Dict]:
        val = info["value"]
        lo, hi = info["normal_min"], info["normal_max"]
        mid = (lo + hi) / 2
        unit = info["unit"]
        if val > hi:
            action = f"Decrease {param} — currently {val-hi:.2f}{unit} above upper limit"
            target_min, target_max = lo, mid
        elif val < lo:
            action = f"Increase {param} — currently {lo-val:.2f}{unit} below lower limit"
            target_min, target_max = mid, hi
        else:
            return None
        return {
            "parameter": param,
            "current": val,
            "target_min": target_min,
            "target_max": target_max,
            "unit": unit,
            "action": action,
            "priority": "CRITICAL" if info["severity"] == "SEVERE" else "MEDIUM",
        }


# Global singleton
_copilot_service: Optional[CopilotService] = None


def get_copilot_service() -> CopilotService:
    """Get or create copilot service singleton."""
    global _copilot_service
    if _copilot_service is None:
        _copilot_service = CopilotService()
    return _copilot_service


if __name__ == "__main__":
    copilot = get_copilot_service()
    test_data = {
        "die_temperature": 195.0, "die_void_percentage": 6.0,
        "wire_pull_strength": 5.0, "inspect_reliability_score": 82.0,
        "predicted_status": "SEVERE",
    }
    resp = copilot.process_query("Why is this batch severe?", {"current_data": test_data})
    print(resp["answer"])

# Made with Bob
