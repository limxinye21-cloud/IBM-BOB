# AI Packaging Reliability Copilot - System Architecture

## Executive Summary

This document defines the complete system architecture for the **AI Packaging Reliability Copilot Powered by IBM Bob** - a production-grade proof-of-concept system for real-time semiconductor packaging monitoring, intelligent diagnosis, and process optimization.

---

## 1. System Overview

### 1.1 Core Objectives

1. **Real-time Monitoring**: Track multi-stage packaging processes with live data ingestion
2. **Intelligent Classification**: Automated status assessment (GOOD/WARNING/SEVERE)
3. **AI-Driven Diagnosis**: Root cause analysis and optimization recommendations via IBM Bob
4. **Proactive Alerting**: Automated notifications with contextual explanations
5. **Historical Intelligence**: Trend analysis and pattern recognition across 100+ hours

### 1.2 Key Differentiators

- **IBM Bob as Intelligent Copilot**: Natural language interaction for process understanding
- **Cross-Stage Reasoning**: Trace defects across the entire manufacturing pipeline
- **Production-Ready Architecture**: Modular, scalable, and extensible design
- **watsonx Integration**: Advanced AI reasoning and workflow orchestration

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Streamlit Dashboard (Frontend)                    │  │
│  │  • Status Light (Good/Warning/Severe)                     │  │
│  │  • Real-time Process Metrics                              │  │
│  │  • Historical Trend Charts (100h)                         │  │
│  │  • Manual Data Input Panel                                │  │
│  │  • AI Copilot Chat Interface                              │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↕ HTTP/WebSocket
┌─────────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         FastAPI Backend (REST API)                        │  │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────┐ │  │
│  │  │ Data Ingestion │  │ Classification │  │  Analysis  │ │  │
│  │  │   Endpoints    │  │   Endpoints    │  │ Endpoints  │ │  │
│  │  └────────────────┘  └────────────────┘  └────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│                     INTELLIGENCE LAYER                          │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │  ML Model    │  │  IBM Bob     │  │  watsonx.ai        │   │
│  │  Pipeline    │  │  Copilot     │  │  Reasoning         │   │
│  │  • Training  │  │  • Context   │  │  • NLP             │   │
│  │  • Inference │  │  • Mapping   │  │  • Explanation     │   │
│  │  • Features  │  │  • RCA       │  │  • Generation      │   │
│  └──────────────┘  └──────────────┘  └────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│                     SERVICE LAYER                               │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │ Data         │  │ Mapping      │  │ Alert Service      │   │
│  │ Processor    │  │ Engine       │  │ • Trigger Logic    │   │
│  │ • Validation │  │ • Issue→Param│  │ • Notification     │   │
│  │ • Transform  │  │ • Cross-Stage│  │ • Orchestrate      │   │
│  └──────────────┘  └──────────────┘  └────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│                     DATA LAYER                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │ PostgreSQL   │  │ Mock Data    │  │ watsonx            │   │
│  │ Database     │  │ Generator    │  │ Orchestrate        │   │
│  │ • Process    │  │ • Real-time  │  │ • Workflows        │   │
│  │ • Historical │  │ • Anomalies  │  │ • Automation       │   │
│  └──────────────┘  └──────────────┘  └────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow Architecture

```
[Mock Data Generator] → [Data Ingestion API] → [Data Processor]
                                                      ↓
                                              [PostgreSQL DB]
                                                      ↓
                                              [ML Inference]
                                                      ↓
                                         [Status Classification]
                                         (GOOD/WARNING/SEVERE)
                                                      ↓
                                    ┌─────────────────┴─────────────────┐
                                    ↓                                   ↓
                            [Dashboard Update]                  [Alert Check]
                                    ↓                                   ↓
                            [User Interface]              [watsonx Orchestrate]
                                    ↓                                   ↓
                            [Bob Copilot Query]           [Notification Send]
                                    ↓
                            [watsonx.ai Reasoning]
                                    ↓
                            [Explanation + Recommendations]
```

---

## 3. Module Breakdown

### 3.1 Data Layer

#### 3.1.1 Mock Data Generator
**Purpose**: Simulate realistic semiconductor packaging process data

**Responsibilities**:
- Generate continuous streaming data for 5 process stages
- Inject realistic anomalies (drift, spikes, instability)
- Model cross-stage dependencies
- Support configurable scenarios (normal, warning, severe)

**Key Parameters by Stage**:
- **Die Attach**: temperature, epoxy_temp, void_percentage, placement_accuracy
- **Wire Bonding**: bonding_force, ultrasonic_power, loop_height, pull_strength
- **Molding**: mold_temp, mold_pressure, fill_time, compound_viscosity
- **Curing**: cure_temp, cure_time, humidity, thermal_profile
- **Inspection**: defect_count, visual_score, electrical_test, reliability_score

#### 3.1.2 PostgreSQL Database
**Purpose**: Structured storage for manufacturing data

**Schema Design**:
```sql
-- Process Data Table
CREATE TABLE process_data (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    machine_id VARCHAR(50),
    process_stage VARCHAR(50),
    status VARCHAR(20),
    parameters JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Alert History Table
CREATE TABLE alert_history (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(50),
    timestamp TIMESTAMP,
    severity VARCHAR(20),
    stage VARCHAR(50),
    message TEXT,
    resolved BOOLEAN DEFAULT FALSE
);

-- Model Predictions Table
CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(50),
    timestamp TIMESTAMP,
    predicted_status VARCHAR(20),
    confidence FLOAT,
    feature_importance JSONB
);
```

### 3.2 Backend Layer (FastAPI)

#### 3.2.1 API Endpoints

**Data Ingestion**:
- `POST /api/v1/data/ingest` - Accept real-time process data
- `POST /api/v1/data/batch` - Batch data upload
- `GET /api/v1/data/stream` - WebSocket for streaming data

**Status & Classification**:
- `GET /api/v1/status/current` - Current system status
- `GET /api/v1/status/batch/{batch_id}` - Batch-specific status
- `POST /api/v1/classify` - Manual classification request

**Analysis & Intelligence**:
- `POST /api/v1/analysis/root-cause` - Root cause analysis
- `POST /api/v1/analysis/stage/{stage}` - Stage-specific analysis
- `GET /api/v1/analysis/trends` - Historical trend analysis

**AI Copilot**:
- `POST /api/v1/copilot/query` - Natural language query
- `POST /api/v1/copilot/explain` - Explain current status
- `POST /api/v1/copilot/optimize` - Get optimization suggestions

**Alerts**:
- `GET /api/v1/alerts/active` - Active alerts
- `GET /api/v1/alerts/history` - Alert history
- `POST /api/v1/alerts/acknowledge` - Acknowledge alert

### 3.3 Intelligence Layer

#### 3.3.1 ML Model Pipeline

**Model Architecture**:
- **Baseline**: RandomForest Classifier
- **Advanced**: LSTM for temporal patterns
- **Features**: 20+ engineered features across all stages

**Training Pipeline**:
1. Feature extraction from multi-stage data
2. Feature engineering (rolling stats, cross-stage ratios)
3. Model training with class balancing
4. Hyperparameter tuning
5. Model validation and persistence

**Inference Pipeline**:
1. Real-time feature computation
2. Model prediction (GOOD/WARNING/SEVERE)
3. Confidence scoring
4. Feature importance extraction

#### 3.3.2 IBM Bob Copilot Engine

**Core Capabilities**:

1. **Context Understanding**:
   - Parse natural language queries
   - Identify relevant process stages
   - Extract intent (diagnosis, optimization, explanation)

2. **Issue-to-Parameter Mapping**:
   ```python
   ISSUE_MAPPING = {
       "die_attach": ["temperature", "epoxy_temp", "void_percentage"],
       "wire_bonding": ["bonding_force", "ultrasonic_power", "loop_height"],
       "molding": ["mold_temp", "mold_pressure", "fill_time"],
       "curing": ["cure_temp", "cure_time", "humidity"]
   }
   ```

3. **Root Cause Analysis**:
   - Identify abnormal parameters
   - Correlate with known failure modes
   - Trace cross-stage dependencies
   - Generate explanations

4. **Optimization Recommendations**:
   - Suggest parameter adjustments
   - Provide confidence levels
   - Reference historical successes

#### 3.3.3 watsonx.ai Integration

**Purpose**: Advanced NLP and reasoning capabilities

**Use Cases**:
- Complex query interpretation
- Context-aware explanation generation
- Multi-turn conversation handling
- Uncertainty reasoning

### 3.4 Presentation Layer (Streamlit)

#### 3.4.1 Dashboard Components

**Status Indicator**:
- Traffic light visualization (Green/Yellow/Red)
- Current batch information
- Last update timestamp

**Real-time Metrics Panel**:
- Live parameter values for all stages
- Trend indicators (↑↓→)
- Threshold violations highlighted

**Historical Analysis**:
- Time-series charts (last 100 hours)
- Status distribution pie chart
- Parameter correlation heatmap

**Data Input Panel**:
- Manual parameter entry
- Scenario selection (normal/warning/severe)
- Batch ID assignment

**AI Copilot Interface**:
- Chat-style interaction
- Pre-defined query buttons
- Explanation display with visualizations

**Alert Dashboard**:
- Active alerts list
- Alert history timeline
- Acknowledgment controls

### 3.5 Service Layer

#### 3.5.1 Data Processor Service

**Responsibilities**:
- Validate incoming data
- Transform to standard format
- Enrich with metadata
- Store in database

#### 3.5.2 Mapping Engine

**Responsibilities**:
- Map issues to relevant parameters
- Identify cross-stage dependencies
- Maintain failure mode knowledge base

#### 3.5.3 Alert Service

**Responsibilities**:
- Monitor for SEVERE conditions
- Generate contextual explanations
- Trigger notifications
- Integrate with watsonx Orchestrate

---

## 4. Technology Stack

### 4.1 Core Technologies

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | FastAPI | High-performance async API |
| **Frontend** | Streamlit | Rapid dashboard development |
| **Database** | PostgreSQL | Structured data storage |
| **ML Framework** | scikit-learn | Classification models |
| **Deep Learning** | TensorFlow/Keras | LSTM models (optional) |
| **AI Platform** | IBM watsonx.ai | Advanced reasoning |
| **Orchestration** | IBM watsonx Orchestrate | Workflow automation |
| **Containerization** | Docker | Deployment packaging |

### 4.2 Python Libraries

```python
# Backend
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9

# Frontend
streamlit==1.28.2
plotly==5.18.0
pandas==2.1.3

# ML/AI
scikit-learn==1.3.2
tensorflow==2.15.0
numpy==1.26.2
scipy==1.11.4

# Data Processing
pandas==2.1.3
numpy==1.26.2

# IBM watsonx
ibm-watson==7.0.1
ibm-watsonx-ai==0.1.0

# Utilities
python-dotenv==1.0.0
requests==2.31.0
websockets==12.0
```

---

## 5. Folder Structure

```
packaging-ai-copilot/
│
├── README.md
├── SYSTEM_ARCHITECTURE.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI application entry
│   │   ├── config.py                  # Configuration management
│   │   ├── dependencies.py            # Dependency injection
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── data.py           # Data ingestion endpoints
│   │   │   │   ├── status.py         # Status endpoints
│   │   │   │   ├── analysis.py       # Analysis endpoints
│   │   │   │   ├── copilot.py        # AI copilot endpoints
│   │   │   │   └── alerts.py         # Alert endpoints
│   │   │   │
│   │   │   └── middleware/
│   │   │       ├── __init__.py
│   │   │       └── logging.py
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── ml_model.py           # ML model definition
│   │   │   ├── inference.py          # Inference pipeline
│   │   │   └── training.py           # Training pipeline
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── data_processor.py     # Data processing logic
│   │   │   ├── mapping_engine.py     # Issue-parameter mapping
│   │   │   ├── copilot.py            # Bob copilot logic
│   │   │   ├── alert_service.py      # Alert management
│   │   │   └── watsonx_service.py    # watsonx integration
│   │   │
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── database.py           # Database connection
│   │   │   ├── models.py             # SQLAlchemy models
│   │   │   └── crud.py               # CRUD operations
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── data_schema.py        # Data models
│   │   │   ├── response_schema.py    # API responses
│   │   │   └── copilot_schema.py     # Copilot models
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── logger.py
│   │       └── validators.py
│   │
│   └── tests/
│       ├── __init__.py
│       ├── test_api.py
│       └── test_services.py
│
├── frontend/
│   ├── dashboard.py                   # Main Streamlit app
│   ├── config.py                      # Frontend config
│   │
│   ├── components/
│   │   ├── __init__.py
│   │   ├── status_light.py           # Status indicator
│   │   ├── metrics_panel.py          # Real-time metrics
│   │   ├── charts.py                 # Visualization components
│   │   ├── input_panel.py            # Data input interface
│   │   ├── chat_copilot.py           # AI chat interface
│   │   └── alerts_panel.py           # Alerts display
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── api_client.py             # Backend API client
│   │   └── formatters.py             # Data formatting
│   │
│   └── assets/
│       ├── styles.css
│       └── logo.png
│
├── data/
│   ├── mock/
│   │   ├── __init__.py
│   │   ├── generator.py              # Real-time data generator
│   │   ├── scenarios.py              # Failure scenarios
│   │   └── config.py                 # Generator configuration
│   │
│   └── sample/
│       └── sample_data.csv
│
├── ml/
│   ├── __init__.py
│   ├── training/
│   │   ├── __init__.py
│   │   ├── train.py                  # Training script
│   │   ├── features.py               # Feature engineering
│   │   └── evaluate.py               # Model evaluation
│   │
│   ├── saved_models/
│   │   └── .gitkeep
│   │
│   └── notebooks/
│       └── exploratory_analysis.ipynb
│
├── orchestrate/
│   ├── workflows/
│   │   ├── alert_workflow.json       # Alert workflow definition
│   │   └── escalation_flow.json     # Escalation workflow
│   │
│   └── skills/
│       └── notification_skill.py
│
├── watsonx/
│   ├── prompts/
│   │   ├── root_cause.txt           # Root cause analysis prompt
│   │   ├── optimization.txt         # Optimization prompt
│   │   └── explanation.txt          # Explanation prompt
│   │
│   └── config/
│       └── watsonx_config.yaml
│
├── bob_sessions/                      # Bob task session reports
│   └── .gitkeep
│
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
│
├── scripts/
│   ├── setup_db.py                   # Database initialization
│   ├── generate_sample_data.py       # Sample data generation
│   └── run_training.py               # ML training script
│
└── docs/
    ├── API_DOCUMENTATION.md
    ├── DEPLOYMENT_GUIDE.md
    └── USER_GUIDE.md
```

---

## 6. Key Design Principles

### 6.1 Modularity
- Each component is independent and replaceable
- Clear interfaces between layers
- Easy to extend with new features

### 6.2 Scalability
- Async API design for high throughput
- Database optimized for time-series queries
- Stateless services for horizontal scaling

### 6.3 Production-Ready
- Comprehensive error handling
- Logging and monitoring
- Configuration management
- Docker containerization

### 6.4 AI-First Design
- IBM Bob integrated at every layer
- Natural language as primary interface
- Context-aware reasoning throughout

---

## 7. Integration Points

### 7.1 IBM Bob Integration

**Development Phase**:
- System architecture design
- Code generation
- Data schema design
- API endpoint creation

**Runtime Phase**:
- Natural language query processing
- Root cause analysis
- Optimization recommendations
- Explanation generation

### 7.2 watsonx.ai Integration

**Capabilities**:
- Advanced NLP for complex queries
- Context-aware response generation
- Multi-turn conversation handling
- Uncertainty reasoning

**API Integration**:
```python
from ibm_watsonx_ai import Credentials, APIClient

credentials = Credentials(
    url="https://us-south.ml.cloud.ibm.com",
    api_key=os.getenv("WATSONX_API_KEY")
)

client = APIClient(credentials)
```

### 7.3 watsonx Orchestrate Integration

**Workflow Automation**:
- Alert notification routing
- Escalation procedures
- Incident logging
- Follow-up task creation

**Workflow Example**:
```json
{
  "name": "Severe Alert Workflow",
  "trigger": "status == SEVERE",
  "steps": [
    {
      "action": "generate_explanation",
      "service": "copilot"
    },
    {
      "action": "send_notification",
      "recipients": ["engineering_manager"]
    },
    {
      "action": "create_incident",
      "system": "ticketing"
    }
  ]
}
```

---

## 8. Data Flow Scenarios

### 8.1 Normal Operation Flow

```
1. Mock Generator → produces normal data
2. API Ingestion → validates and stores
3. ML Model → predicts GOOD status
4. Dashboard → displays green light
5. Historical DB → stores for trend analysis
```

### 8.2 Anomaly Detection Flow

```
1. Mock Generator → injects anomaly
2. API Ingestion → detects unusual values
3. ML Model → predicts WARNING/SEVERE
4. Alert Service → checks severity
5. If SEVERE:
   a. Bob Copilot → generates explanation
   b. watsonx Orchestrate → triggers workflow
   c. Notification → sent to manager
6. Dashboard → updates status light
7. User → queries Bob for details
8. Bob → provides root cause analysis
```

### 8.3 User Query Flow

```
1. User → asks "Why is this batch severe?"
2. Dashboard → sends query to copilot API
3. Copilot Service → retrieves relevant data
4. Mapping Engine → identifies key parameters
5. watsonx.ai → generates explanation
6. Copilot → formats response
7. Dashboard → displays explanation with charts
```

---

## 9. Security & Compliance

### 9.1 Authentication
- API key authentication for backend
- Role-based access control (RBAC)
- Secure credential management

### 9.2 Data Privacy
- No PII in manufacturing data
- Encrypted database connections
- Audit logging for all operations

### 9.3 Monitoring
- Application performance monitoring
- Error tracking and alerting
- Usage analytics

---

## 10. Deployment Strategy

### 10.1 Local Development
```bash
# Backend
cd backend
uvicorn app.main:app --reload

# Frontend
cd frontend
streamlit run dashboard.py

# Database
docker-compose up postgres
```

### 10.2 Production Deployment

**Option 1: Docker Compose**
```bash
docker-compose up -d
```

**Option 2: Cloud Deployment**
- Backend: IBM Cloud Code Engine / Railway
- Frontend: Streamlit Cloud / Render
- Database: IBM Cloud Databases for PostgreSQL

---

## 11. Success Metrics

### 11.1 Technical Metrics
- API response time < 200ms
- Dashboard refresh rate: 1-2 seconds
- ML inference time < 100ms
- 99.9% uptime

### 11.2 Business Metrics
- Time to detect anomaly: < 5 seconds
- Time to diagnose root cause: < 30 seconds
- False positive rate: < 5%
- User satisfaction score: > 4.5/5

---

## 12. Future Enhancements

### 12.1 Phase 2 Features
- Real sensor integration (OPC-UA, MQTT)
- Advanced LSTM models for prediction
- Multi-factory deployment
- Mobile app for alerts

### 12.2 Phase 3 Features
- Predictive maintenance
- Automated parameter optimization
- Digital twin integration
- AR/VR visualization

---

## 13. Conclusion

This architecture provides a solid foundation for building a production-grade AI Packaging Reliability Copilot. The modular design ensures scalability, the IBM Bob integration enables intelligent interaction, and the watsonx platform provides enterprise-grade AI capabilities.

The system is designed to be:
- **Demonstrable**: Clear value proposition for hackathon judges
- **Extensible**: Easy to add new features and integrations
- **Production-Ready**: Follows best practices for real-world deployment
- **AI-First**: IBM Bob and watsonx at the core of the solution

---

**Next Steps**: Proceed to STEP 2 - Data Schema & Process Intelligence Design