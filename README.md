# AI Packaging Reliability Copilot — Powered by IBM Bob

**Real-time Semiconductor Packaging Monitoring & AI Copilot System**

[![Python](https://img.shields.io/badge/Python-3.11.9-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28-red.svg)](https://streamlit.io/)
[![IBM Bob](https://img.shields.io/badge/Built%20with-IBM%20Bob-0f62fe.svg)](https://www.ibm.com/bob)
[![Hackathon](https://img.shields.io/badge/IBM%20Bob%20Dev%20Day-Hackathon%202026-purple.svg)]()

> **Hackathon Theme**: *Turn idea into impact faster* — IBM Bob Dev Day 2026

---

## Project Overview

The **AI Packaging Reliability Copilot** is a production-grade proof-of-concept demonstrating how AI
can transform semiconductor manufacturing operations. Built entirely with **IBM Bob IDE** as the core
development partner, this system monitors multi-stage packaging processes in real-time, predicts
reliability issues, and provides actionable insights through a natural language copilot.

### Key Innovation

Unlike traditional monitoring systems that only display data, this system **understands** the
manufacturing process through AI-powered analysis:
- **Early defect detection** before downstream inspection
- **Root cause analysis** across 5 packaging stages
- **Natural language copilot** — ask questions, get manufacturing insights
- **Forecasting** — linear regression trend prediction across cycles

---

## Built with IBM Bob IDE

Every component of this system was built using **IBM Bob IDE** as the intelligent development partner:

| What Bob Built | Details |
|---|---|
| ML ensemble pipeline | VotingClassifier (RF + GradientBoosting) + IsolationForest, 49 features |
| NL Copilot service | 8 query handlers (health, why, forecast, recommend, explain, analyze, compare, general) |
| IBM Carbon light UI | Full IBM professional theme — KPI bar, stage flow cards, responsive layout |
| FastAPI backend | 20+ REST endpoints across data, ML, copilot, and alerts routes |
| 3 custom Bob agents | debug.agent.md, ml-trainer.agent.md, understand-code.agent.md |
| AGENTS.md | Persistent project context for Bob across sessions |
| Bug fixes | Fixed inference.py dict literal, copilot_service.py duplicate code cleanup |

**Bob sessions**: `bob_sessions/` — 10 exported task sessions (required for hackathon judging)

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the full system (backend + dashboard)
python run.py

# 3. Open in browser
# Dashboard:   http://localhost:8501
# API docs:    http://localhost:8000/docs
```

### Optional: Enable watsonx.ai (IBM Granite model)
```bash
export WATSONX_API_KEY="your-ibm-cloud-api-key"
export WATSONX_PROJECT_ID="your-watsonx-project-id"
python run.py
```
When set, the AI Copilot routes NL responses through IBM Granite (`ibm/granite-13b-instruct-v2`).
Falls back to rule-based engine when credentials are not set.

---

## Key Features

### Real-Time Monitoring
- **33 process parameters** across 5 packaging stages
- **Animated status indicators** — GOOD / WARNING / SEVERE with color-specific pulse animations
- **7-tab dashboard** — Parameters, ML Analysis, AI Copilot, Alerts, Trends, Manual Input, Data Details
- **KPI hero bar** — 6 live metric cards (Status, ML Confidence, Reliability, Defects, Void%, Batch ID)
- **Stage health flow** — 5 stage cards with 0–100 health scores and progress bars

### AI-Powered Classification
- **Ensemble ML model**: `CalibratedClassifierCV(VotingClassifier([RandomForest, GradientBoosting]))`
- **Anomaly detector**: IsolationForest for unsupervised outlier detection
- **Test accuracy**: ~90.75% (baseline); retrain with `python ml/training/train.py` for full ensemble
- **Confidence scores** with probability breakdown per class

### Explainable AI
- **Stage Health Radar** — polar chart showing 0–100 health per stage
- **Parameter Deviation Heatmap** — 18 parameters, % deviation from normal range (green→red)
- **Feature importance** — top-10 contributors ranked by importance
- **Critical parameter flagging** — highlights parameters with importance ≥ 5%

### AI Copilot (Natural Language)
- **8 query handlers** for manufacturing intelligence
- **IBM-styled chat UI** — dark user bubbles, white bot bubbles with IBM blue left border
- **Follow-up chips** — context-aware suggestions after each response
- **Quick actions** — preset buttons for common queries
- **Trend forecasting** — linear regression across last 10 cycles
- **watsonx.ai ready** — IBM Granite model integration (set env vars to enable)

### Alerts & Monitoring
- **Active alerts panel** — severity badges (IBM Carbon palette), acknowledge + workflow actions
- **Alert statistics** — 24-hour summary with severity distribution
- **Alert history** — timeline with colored IBM-styled entries
- **Manual alert check** — trigger via current process data

### Scenario Simulation
- **8 predefined scenarios**: Normal, wire_bonding_failure, die_attach_void, mold_void_formation,
  thermal_runaway, cure_incomplete, multi_stage_degradation, inspection_failure
- **Quick Fill buttons** in Manual Input — Normal / Wire Fail / Die Void / Mold Issue presets
- **Inline validation** — warns on dangerous parameter combinations

---

## System Architecture

```
┌────────────────────────────────────────────────────────┐
│               PRESENTATION LAYER                        │
│  Streamlit Dashboard (Port 8501)                        │
│  IBM Carbon Light Theme | 7 Tabs | KPI Bar | Chat UI   │
└───────────────────────┬────────────────────────────────┘
                        │ HTTP/REST
┌───────────────────────▼────────────────────────────────┐
│               APPLICATION LAYER                         │
│  FastAPI Backend (Port 8000)                            │
│  /data  /ml  /copilot  /alerts  /health                │
└───────────────────────┬────────────────────────────────┘
                        │
┌───────────────────────▼────────────────────────────────┐
│               INTELLIGENCE LAYER                        │
│  CopilotService (8 NL handlers + watsonx.ai stub)      │
│  ModelInference (Ensemble + IsolationForest)            │
│  FeatureEngineer (49 features)                          │
└───────────────────────┬────────────────────────────────┘
                        │
┌───────────────────────▼────────────────────────────────┐
│               DATA LAYER                                │
│  SQLite (packaging.db) | MockDataGenerator (33 params) │
└────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
IBM BOB/
├── backend/app/
│   ├── api/routes/          # data.py, ml.py, copilot.py, alerts.py
│   ├── services/            # ml_service.py, copilot_service.py, alert_service.py
│   └── db/                  # database.py, models.py
├── frontend/
│   ├── dashboard.py         # Main dashboard — 7 tabs, KPI bar, IBM light theme
│   └── components/          # charts.py, chat_copilot.py, alerts_panel.py, status_light.py
├── ml/
│   ├── training/            # train.py, inference.py, features.py
│   └── saved_models/        # model_latest.joblib, feature_engineer_latest.joblib
├── data/mock/               # generator.py, scenarios.py (8 failure modes)
├── bob_sessions/            # IBM Bob task session exports (judging requirement)
├── .github/agents/          # debug.agent.md, ml-trainer.agent.md, understand-code.agent.md
├── AGENTS.md                # Bob /init project context
├── requirements.txt
└── run.py                   # Starts both backend + frontend
```

---

## Development Phases

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1 | ✅ Complete | Dashboard, ML classification, feature importance, 8 scenarios, FastAPI backend |
| Phase 2 | ✅ Complete | NL Copilot (8 handlers), IBM light theme, stage health radar, alerts panel, ensemble ML |
| Phase 2.5 | ✅ Complete | AGENTS.md, custom Bob agents, watsonx.ai stub, Manual Input Quick Fill |
| Phase 3 | 🔜 Planned | LSTM time-series forecasting, real sensor integration |
| Phase 4 | 🔜 Planned | Digital twin, watsonx Orchestrate workflows |

---

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | System health check |
| `/data/process` | POST | Submit process data |
| `/ml/predict` | POST | Get ML prediction |
| `/ml/explain` | POST | Feature importance |
| `/ml/status` | GET | Model load status |
| `/copilot/query` | POST | Natural language query |
| `/copilot/root-cause` | POST | Root cause analysis |
| `/copilot/optimize` | POST | Optimization recommendations |
| `/alerts/active` | GET | Active alerts list |
| `/alerts/{id}/acknowledge` | POST | Acknowledge alert |
| `/alerts/check` | POST | Check current data for alerts |

---

## IBM Bob Hackathon Submission

**Hackathon**: IBM Bob Dev Day 2026  
**Theme**: Turn idea into impact faster  
**Core product**: IBM Bob IDE (required)  
**Optional products**: watsonx.ai (Granite model stub integrated), watsonx Orchestrate (planned)

### Judging Requirements
- [x] IBM Bob IDE used as core development partner
- [x] Bob task session `.md` files in `bob_sessions/` (10 sessions)
- [ ] Task session consumption **screenshots** in `bob_sessions/` ← *manual step: Bob IDE → History → click task header → screenshot*
- [x] `AGENTS.md` for persistent project context
- [x] watsonx.ai integration (stub — set env vars to activate Granite model)

---

*Built with IBM Bob IDE · watsonx.ai · Python 3.11.9 · FastAPI · Streamlit · scikit-learn*
