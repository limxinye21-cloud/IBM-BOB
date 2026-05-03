"""
Scenario-aware copilot and alert validation test
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from backend.app.services.copilot_service import get_copilot_service, SCENARIO_PROFILES
from backend.app.services.alert_service import AlertService

copilot = get_copilot_service()
alert_svc = AlertService()

print("=" * 60)
print("SCENARIO PROFILES LOADED:", list(SCENARIO_PROFILES.keys()))
print("ALERT RULES LOADED:", list(alert_svc.alert_rules.keys()))
print(f"Total alert rules: {len(alert_svc.alert_rules)}")
print()

# --- Scenario Detection Tests ---
scenarios_to_test = [
    ("wire_bonding_failure", {
        "wire_pull_strength": 4.5, "wire_bonding_force": 30.0,
        "wire_ultrasonic_power": 60.0, "predicted_status": "SEVERE",
        "confidence": 0.91, "batch_id": "B001"
    }),
    ("curing_incomplete", {
        "cure_time": 90, "cure_temperature": 172, "cure_uniformity": 3.1,
        "predicted_status": "SEVERE", "confidence": 0.88
    }),
    ("cascading_failure", {
        "die_void_percentage": 7, "wire_pull_strength": 3.5,
        "inspect_reliability_score": 72, "inspect_defect_count": 5,
        "predicted_status": "SEVERE", "confidence": 0.97
    }),
    ("die_attach_drift", {
        "die_temperature": 198, "die_void_percentage": 4.5,
        "predicted_status": "WARNING", "confidence": 0.75
    }),
    ("molding_issue", {
        "mold_voids": 2.0, "mold_compound_viscosity": 170,
        "predicted_status": "SEVERE", "confidence": 0.85
    }),
    ("inspection_failure", {
        "inspect_defect_count": 5, "inspect_electrical_test": 0,
        "inspect_reliability_score": 72, "predicted_status": "SEVERE",
        "confidence": 0.93
    }),
    ("intermittent_warning", {
        "wire_bonding_force": 38, "wire_ultrasonic_power": 80,
        "predicted_status": "WARNING", "confidence": 0.65
    }),
    ("normal", {
        "die_temperature": 185, "wire_pull_strength": 10,
        "mold_voids": 0.5, "cure_time": 150,
        "inspect_reliability_score": 96, "predicted_status": "GOOD",
        "confidence": 0.92
    }),
]

print("--- Scenario Detection ---")
for expected_key, data in scenarios_to_test:
    key, profile, conf = copilot._detect_scenario(data)
    match = "PASS" if key == expected_key else f"FAIL (got {key})"
    print(f"  [{match}] Expected={expected_key} -> Detected={key} ({conf:.0%}) : {profile['name']}")

print()

# --- Alert Rule Tests ---
print("--- Alert Rules ---")
alert_tests = [
    ("cascading", {"die_void_percentage": 7, "wire_pull_strength": 3.5,
                   "inspect_reliability_score": 72, "predicted_status": "SEVERE",
                   "batch_id": "B01", "machine_id": "M01"},
     ["CRITICAL: Cascading Multi-Stage Failure"]),
    ("curing", {"cure_time": 90, "cure_temperature": 172, "predicted_status": "SEVERE",
                "batch_id": "B02", "machine_id": "M01"},
     ["Incomplete Curing Detected"]),
    ("molding viscosity", {"mold_compound_viscosity": 170, "mold_voids": 1.8,
                           "predicted_status": "WARNING", "batch_id": "B03", "machine_id": "M01"},
     ["Molding Compound Viscosity Out of Spec", "Elevated Mold Void Percentage"]),
]
for name, data, expected_titles in alert_tests:
    alerts = alert_svc.check_alerts(data)
    titles = [a["title"] for a in alerts]
    for expected in expected_titles:
        match = "PASS" if expected in titles else "FAIL"
        print(f"  [{match}] {name}: '{expected}'")

print()

# --- Handler Tests ---
print("--- Copilot Handlers ---")
handler_tests = [
    ("why", "Why is this batch severe?",
     {"wire_pull_strength": 4.5, "wire_bonding_force": 30, "predicted_status": "SEVERE",
      "confidence": 0.91, "batch_id": "B01"}, "why", "wire_bonding_failure"),
    ("recommend", "How can I fix this?",
     {"cure_time": 90, "cure_temperature": 172, "predicted_status": "SEVERE",
      "confidence": 0.88}, "recommendation", "curing_incomplete"),
    ("decision", "Give me a full assessment",
     {"die_void_percentage": 7, "wire_pull_strength": 3.5,
      "inspect_reliability_score": 72, "predicted_status": "SEVERE",
      "confidence": 0.97}, "decision", "cascading_failure"),
    ("general", "Hello, what can you do?",
     {"predicted_status": "GOOD", "confidence": 0.92}, "general", None),
]
for name, query, data, expected_type, expected_scenario in handler_tests:
    resp = copilot.process_query(query, {"current_data": data})
    t_match = "PASS" if resp["type"] == expected_type else f"FAIL (got {resp['type']})"
    s_match = ""
    if expected_scenario:
        detected = resp.get("detected_scenario", "n/a")
        s_match = f" | scenario={'PASS' if detected == expected_scenario else 'FAIL got ' + detected}"
    print(f"  [{t_match}] {name}: type={resp['type']}{s_match}")

print()
print("Validation complete.")
