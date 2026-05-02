# AI Packaging Reliability Copilot - Architecture Diagrams

## 1. System Context Diagram

```mermaid
graph TB
    subgraph "External Systems"
        USER[Engineering Manager/Process Engineer]
        SENSORS[Manufacturing Sensors<br/>Future Integration]
        NOTIFY[Notification Systems<br/>Email/Slack/SMS]
    end
    
    subgraph "AI Packaging Reliability Copilot"
        DASHBOARD[Streamlit Dashboard]
        API[FastAPI Backend]
        DB[(PostgreSQL Database)]
        ML[ML Classification Engine]
        BOB[IBM Bob Copilot]
        WATSON[watsonx.ai]
        ORCH[watsonx Orchestrate]
        MOCK[Mock Data Generator]
    end
    
    USER -->|Interact| DASHBOARD
    USER -->|Query| BOB
    SENSORS -.->|Future| API
    MOCK -->|Simulate Data| API
    DASHBOARD <-->|REST API| API
    API <-->|Store/Retrieve| DB
    API -->|Classify| ML
    API -->|Analyze| BOB
    BOB <-->|Reasoning| WATSON
    API -->|Trigger| ORCH
    ORCH -->|Send| NOTIFY
```

## 2. Component Architecture

```mermaid
graph TB
    subgraph "Presentation Layer"
        UI[Streamlit Dashboard]
        STATUS[Status Light Component]
        METRICS[Metrics Panel]
        CHARTS[Historical Charts]
        INPUT[Data Input Panel]
        CHAT[AI Copilot Chat]
        ALERTS[Alerts Panel]
    end
    
    subgraph "API Layer"
        ROUTES[API Routes]
        DATA_EP[Data Endpoints]
        STATUS_EP[Status Endpoints]
        ANALYSIS_EP[Analysis Endpoints]
        COPILOT_EP[Copilot Endpoints]
        ALERT_EP[Alert Endpoints]
    end
    
    subgraph "Service Layer"
        PROCESSOR[Data Processor]
        MAPPER[Mapping Engine]
        COPILOT_SVC[Copilot Service]
        ALERT_SVC[Alert Service]
        WATSON_SVC[watsonx Service]
    end
    
    subgraph "Intelligence Layer"
        ML_MODEL[ML Model]
        INFERENCE[Inference Pipeline]
        BOB_ENGINE[Bob Reasoning Engine]
        WATSON_AI[watsonx.ai NLP]
    end
    
    subgraph "Data Layer"
        DATABASE[(PostgreSQL)]
        MOCK_GEN[Mock Generator]
        SCENARIOS[Failure Scenarios]
    end
    
    UI --> ROUTES
    ROUTES --> DATA_EP & STATUS_EP & ANALYSIS_EP & COPILOT_EP & ALERT_EP
    DATA_EP --> PROCESSOR
    STATUS_EP --> INFERENCE
    ANALYSIS_EP --> COPILOT_SVC
    COPILOT_EP --> BOB_ENGINE
    ALERT_EP --> ALERT_SVC
    
    PROCESSOR --> DATABASE
    INFERENCE --> ML_MODEL
    COPILOT_SVC --> MAPPER
    BOB_ENGINE --> WATSON_AI
    ALERT_SVC --> WATSON_SVC
    
    MOCK_GEN --> DATA_EP
    SCENARIOS --> MOCK_GEN
```

## 3. Data Flow Architecture

```mermaid
sequenceDiagram
    participant MG as Mock Generator
    participant API as FastAPI
    participant DB as PostgreSQL
    participant ML as ML Model
    participant DASH as Dashboard
    participant BOB as Bob Copilot
    participant WX as watsonx.ai
    participant ORCH as Orchestrate
    
    Note over MG,ORCH: Normal Operation Flow
    MG->>API: POST /api/v1/data/ingest
    API->>DB: Store process data
    API->>ML: Classify status
    ML-->>API: GOOD/WARNING/SEVERE
    API->>DB: Store prediction
    API-->>DASH: Update status
    DASH->>DASH: Display green light
    
    Note over MG,ORCH: Anomaly Detection Flow
    MG->>API: POST /api/v1/data/ingest (anomaly)
    API->>DB: Store anomalous data
    API->>ML: Classify status
    ML-->>API: SEVERE
    API->>BOB: Generate explanation
    BOB->>WX: Request reasoning
    WX-->>BOB: Root cause analysis
    BOB-->>API: Explanation + recommendations
    API->>ORCH: Trigger alert workflow
    ORCH->>ORCH: Send notifications
    API-->>DASH: Update to red light
    
    Note over MG,ORCH: User Query Flow
    DASH->>API: POST /api/v1/copilot/query
    API->>BOB: Process query
    BOB->>DB: Retrieve relevant data
    BOB->>WX: Generate explanation
    WX-->>BOB: Contextual response
    BOB-->>API: Formatted answer
    API-->>DASH: Display response
```

## 4. ML Pipeline Architecture

```mermaid
graph LR
    subgraph "Training Phase"
        HIST[Historical Data] --> FEAT[Feature Engineering]
        FEAT --> TRAIN[Model Training]
        TRAIN --> EVAL[Evaluation]
        EVAL --> SAVE[Save Model]
    end
    
    subgraph "Inference Phase"
        REALTIME[Real-time Data] --> EXTRACT[Feature Extraction]
        EXTRACT --> LOAD[Load Model]
        LOAD --> PREDICT[Prediction]
        PREDICT --> CONF[Confidence Score]
        CONF --> CLASS[Classification]
    end
    
    subgraph "Features"
        F1[Temperature Stats]
        F2[Pressure Ratios]
        F3[Time Deltas]
        F4[Cross-Stage Metrics]
        F5[Rolling Averages]
    end
    
    FEAT --> F1 & F2 & F3 & F4 & F5
    EXTRACT --> F1 & F2 & F3 & F4 & F5
```

## 5. Database Schema Diagram

```mermaid
erDiagram
    PROCESS_DATA ||--o{ PREDICTIONS : has
    PROCESS_DATA ||--o{ ALERT_HISTORY : triggers
    PROCESS_DATA {
        int id PK
        string batch_id
        timestamp timestamp
        string machine_id
        string process_stage
        string status
        jsonb parameters
        timestamp created_at
    }
    
    PREDICTIONS {
        int id PK
        string batch_id FK
        timestamp timestamp
        string predicted_status
        float confidence
        jsonb feature_importance
    }
    
    ALERT_HISTORY {
        int id PK
        string batch_id FK
        timestamp timestamp
        string severity
        string stage
        text message
        boolean resolved
    }
    
    MODEL_METADATA {
        int id PK
        string model_version
        timestamp trained_at
        float accuracy
        jsonb metrics
    }
```

## 6. IBM Bob Integration Points

```mermaid
graph TB
    subgraph "Development Phase"
        ARCH[Architecture Design]
        CODE[Code Generation]
        SCHEMA[Schema Design]
        API_GEN[API Generation]
        TEST[Test Generation]
    end
    
    subgraph "Runtime Phase"
        QUERY[Query Processing]
        RCA[Root Cause Analysis]
        OPT[Optimization Suggestions]
        EXPLAIN[Explanation Generation]
    end
    
    subgraph "IBM Bob"
        BOB_DEV[Bob Development Mode]
        BOB_RUN[Bob Runtime Engine]
    end
    
    BOB_DEV --> ARCH & CODE & SCHEMA & API_GEN & TEST
    BOB_RUN --> QUERY & RCA & OPT & EXPLAIN
    
    QUERY --> CONTEXT[Context Understanding]
    RCA --> MAPPING[Parameter Mapping]
    OPT --> RECOMMEND[Recommendation Engine]
    EXPLAIN --> WATSON[watsonx.ai]
```

## 7. Alert Workflow

```mermaid
stateDiagram-v2
    [*] --> Monitoring
    Monitoring --> Normal: Status = GOOD
    Monitoring --> Warning: Status = WARNING
    Monitoring --> Severe: Status = SEVERE
    
    Normal --> Monitoring: Continue
    Warning --> Monitoring: Resolved
    Warning --> Severe: Degraded
    
    Severe --> GenerateExplanation
    GenerateExplanation --> TriggerWorkflow
    TriggerWorkflow --> SendNotification
    SendNotification --> CreateIncident
    CreateIncident --> WaitAcknowledgment
    WaitAcknowledgment --> Resolved: Acknowledged
    Resolved --> Monitoring
    
    Severe --> [*]: Critical Failure
```

## 8. Deployment Architecture

```mermaid
graph TB
    subgraph "Production Environment"
        subgraph "Container Orchestration"
            LB[Load Balancer]
            
            subgraph "Backend Cluster"
                API1[FastAPI Instance 1]
                API2[FastAPI Instance 2]
                API3[FastAPI Instance 3]
            end
            
            subgraph "Frontend"
                DASH1[Streamlit Instance]
            end
            
            subgraph "Data Services"
                DB[(PostgreSQL)]
                REDIS[(Redis Cache)]
            end
            
            subgraph "ML Services"
                ML_SVC[ML Inference Service]
            end
        end
        
        subgraph "External Services"
            WATSON_AI[watsonx.ai]
            ORCH_SVC[watsonx Orchestrate]
        end
    end
    
    LB --> API1 & API2 & API3
    LB --> DASH1
    API1 & API2 & API3 --> DB
    API1 & API2 & API3 --> REDIS
    API1 & API2 & API3 --> ML_SVC
    API1 & API2 & API3 --> WATSON_AI
    API1 & API2 & API3 --> ORCH_SVC
    DASH1 --> LB
```

## 9. Security Architecture

```mermaid
graph TB
    subgraph "Security Layers"
        AUTH[Authentication Layer]
        AUTHZ[Authorization Layer]
        ENCRYPT[Encryption Layer]
        AUDIT[Audit Layer]
    end
    
    subgraph "Security Components"
        API_KEY[API Key Management]
        RBAC[Role-Based Access Control]
        TLS[TLS/SSL Encryption]
        LOG[Audit Logging]
    end
    
    AUTH --> API_KEY
    AUTHZ --> RBAC
    ENCRYPT --> TLS
    AUDIT --> LOG
    
    USER[User] --> AUTH
    AUTH --> AUTHZ
    AUTHZ --> APP[Application]
    APP --> ENCRYPT
    ENCRYPT --> DATA[(Data)]
    APP --> AUDIT
```

## 10. Monitoring & Observability

```mermaid
graph TB
    subgraph "Application"
        APP[FastAPI Application]
        DASH[Streamlit Dashboard]
    end
    
    subgraph "Monitoring Stack"
        METRICS[Metrics Collection]
        LOGS[Log Aggregation]
        TRACES[Distributed Tracing]
        ALERTS_MON[Alert Manager]
    end
    
    subgraph "Visualization"
        GRAFANA[Grafana Dashboards]
        KIBANA[Kibana Logs]
    end
    
    APP --> METRICS
    APP --> LOGS
    APP --> TRACES
    DASH --> METRICS
    DASH --> LOGS
    
    METRICS --> GRAFANA
    LOGS --> KIBANA
    TRACES --> GRAFANA
    
    METRICS --> ALERTS_MON
    ALERTS_MON --> NOTIFY[Notifications]
```

---

## Diagram Explanations

### System Context Diagram
Shows the high-level interaction between users, external systems, and the AI Packaging Reliability Copilot platform.

### Component Architecture
Illustrates the internal structure of the system, showing how different layers and components interact.

### Data Flow Architecture
Demonstrates the sequence of operations for normal operation, anomaly detection, and user queries.

### ML Pipeline Architecture
Details the machine learning workflow from training to inference, including feature engineering.

### Database Schema Diagram
Shows the relational structure of the database, including tables and their relationships.

### IBM Bob Integration Points
Highlights where IBM Bob is used during development and runtime phases.

### Alert Workflow
State diagram showing the alert lifecycle from detection to resolution.

### Deployment Architecture
Production deployment setup with load balancing, clustering, and external service integration.

### Security Architecture
Security layers and components ensuring system protection.

### Monitoring & Observability
Monitoring infrastructure for system health and performance tracking.

---

## Key Architectural Decisions

### 1. Microservices vs Monolith
**Decision**: Modular monolith for hackathon, designed for microservices migration
**Rationale**: Faster development while maintaining clear boundaries

### 2. Database Choice
**Decision**: PostgreSQL
**Rationale**: JSONB support for flexible parameter storage, strong ACID compliance

### 3. Real-time Communication
**Decision**: HTTP polling initially, WebSocket for future
**Rationale**: Simpler implementation, adequate for demo

### 4. ML Model Deployment
**Decision**: In-process inference
**Rationale**: Lower latency, simpler deployment for POC

### 5. Frontend Framework
**Decision**: Streamlit
**Rationale**: Rapid development, Python-native, excellent for data visualization

---

**Status**: Architecture diagrams complete ✅
**Next**: Clarifying questions and data schema design