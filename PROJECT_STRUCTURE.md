# AI Packaging Reliability Copilot - Project Structure

## Complete Folder Structure

This document provides the detailed folder structure for the entire project, with explanations for each component.

```
packaging-ai-copilot/
│
├── README.md                          # Project overview and setup instructions
├── SYSTEM_ARCHITECTURE.md             # Complete system architecture (this document)
├── PROJECT_STRUCTURE.md               # Folder structure explanation
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment variables template
├── .gitignore                         # Git ignore rules
├── LICENSE                            # Project license
│
├── backend/                           # Backend API and services
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI application entry point
│   │   ├── config.py                 # Configuration management (env vars, settings)
│   │   ├── dependencies.py           # Dependency injection for FastAPI
│   │   │
│   │   ├── api/                      # API layer
│   │   │   ├── __init__.py
│   │   │   ├── routes/               # API route definitions
│   │   │   │   ├── __init__.py
│   │   │   │   ├── data.py          # Data ingestion endpoints
│   │   │   │   ├── status.py        # Status query endpoints
│   │   │   │   ├── analysis.py      # Analysis endpoints
│   │   │   │   ├── copilot.py       # AI copilot endpoints
│   │   │   │   └── alerts.py        # Alert management endpoints
│   │   │   │
│   │   │   └── middleware/           # API middleware
│   │   │       ├── __init__.py
│   │   │       ├── logging.py       # Request/response logging
│   │   │       └── error_handler.py # Global error handling
│   │   │
│   │   ├── models/                   # ML models
│   │   │   ├── __init__.py
│   │   │   ├── ml_model.py          # ML model class definition
│   │   │   ├── inference.py         # Real-time inference pipeline
│   │   │   └── training.py          # Model training pipeline
│   │   │
│   │   ├── services/                 # Business logic layer
│   │   │   ├── __init__.py
│   │   │   ├── data_processor.py    # Data validation and transformation
│   │   │   ├── mapping_engine.py    # Issue-to-parameter mapping logic
│   │   │   ├── copilot.py           # Bob copilot reasoning engine
│   │   │   ├── alert_service.py     # Alert generation and management
│   │   │   └── watsonx_service.py   # watsonx.ai integration service
│   │   │
│   │   ├── db/                       # Database layer
│   │   │   ├── __init__.py
│   │   │   ├── database.py          # Database connection and session management
│   │   │   ├── models.py            # SQLAlchemy ORM models
│   │   │   └── crud.py              # CRUD operations
│   │   │
│   │   ├── schemas/                  # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── data_schema.py       # Data models for process data
│   │   │   ├── response_schema.py   # API response models
│   │   │   └── copilot_schema.py    # Copilot request/response models
│   │   │
│   │   └── utils/                    # Utility functions
│   │       ├── __init__.py
│   │       ├── logger.py            # Logging configuration
│   │       └── validators.py        # Custom validators
│   │
│   └── tests/                        # Backend tests
│       ├── __init__.py
│       ├── test_api.py              # API endpoint tests
│       ├── test_services.py         # Service layer tests
│       └── test_models.py           # Model tests
│
├── frontend/                         # Streamlit dashboard
│   ├── dashboard.py                 # Main Streamlit application
│   ├── config.py                    # Frontend configuration
│   │
│   ├── components/                  # Reusable UI components
│   │   ├── __init__.py
│   │   ├── status_light.py         # Traffic light status indicator
│   │   ├── metrics_panel.py        # Real-time metrics display
│   │   ├── charts.py               # Chart components (plotly)
│   │   ├── input_panel.py          # Manual data input interface
│   │   ├── chat_copilot.py         # AI chat interface
│   │   └── alerts_panel.py         # Alerts display panel
│   │
│   ├── utils/                       # Frontend utilities
│   │   ├── __init__.py
│   │   ├── api_client.py           # Backend API client
│   │   └── formatters.py           # Data formatting utilities
│   │
│   └── assets/                      # Static assets
│       ├── styles.css              # Custom CSS
│       ├── logo.png                # IBM/Project logo
│       └── icons/                  # UI icons
│
├── data/                            # Data generation and samples
│   ├── mock/                       # Mock data generator
│   │   ├── __init__.py
│   │   ├── generator.py           # Real-time data generator
│   │   ├── scenarios.py           # Predefined failure scenarios
│   │   └── config.py              # Generator configuration
│   │
│   └── sample/                     # Sample datasets
│       ├── sample_data.csv        # Sample historical data
│       └── training_data.csv      # Training dataset
│
├── ml/                             # Machine learning components
│   ├── __init__.py
│   ├── training/                  # Training scripts
│   │   ├── __init__.py
│   │   ├── train.py              # Main training script
│   │   ├── features.py           # Feature engineering
│   │   └── evaluate.py           # Model evaluation
│   │
│   ├── saved_models/              # Trained model artifacts
│   │   ├── .gitkeep
│   │   └── model_v1.pkl          # Saved model (generated)
│   │
│   └── notebooks/                 # Jupyter notebooks
│       ├── exploratory_analysis.ipynb
│       └── model_experiments.ipynb
│
├── orchestrate/                    # watsonx Orchestrate workflows
│   ├── workflows/                 # Workflow definitions
│   │   ├── alert_workflow.json   # Alert notification workflow
│   │   └── escalation_flow.json  # Escalation workflow
│   │
│   └── skills/                    # Custom skills
│       ├── __init__.py
│       └── notification_skill.py # Notification skill implementation
│
├── watsonx/                        # watsonx.ai configuration
│   ├── prompts/                   # Prompt templates
│   │   ├── root_cause.txt        # Root cause analysis prompt
│   │   ├── optimization.txt      # Optimization prompt
│   │   └── explanation.txt       # Explanation generation prompt
│   │
│   └── config/                    # watsonx configuration
│       └── watsonx_config.yaml   # API keys and settings
│
├── bob_sessions/                   # IBM Bob session reports (for judging)
│   ├── .gitkeep
│   └── session_reports/           # Exported session reports
│
├── docker/                         # Docker configuration
│   ├── Dockerfile.backend         # Backend container
│   ├── Dockerfile.frontend        # Frontend container
│   └── docker-compose.yml         # Multi-container orchestration
│
├── scripts/                        # Utility scripts
│   ├── setup_db.py               # Database initialization
│   ├── generate_sample_data.py   # Generate sample data
│   ├── run_training.py           # Run ML training
│   └── deploy.sh                 # Deployment script
│
└── docs/                          # Documentation
    ├── API_DOCUMENTATION.md      # API reference
    ├── DEPLOYMENT_GUIDE.md       # Deployment instructions
    ├── USER_GUIDE.md             # User manual
    └── DEMO_SCRIPT.md            # Demo presentation script
```

---

## Module Responsibilities

### Backend (`/backend`)

**Purpose**: Core API and business logic

**Key Components**:
- **API Routes**: RESTful endpoints for all operations
- **Services**: Business logic and orchestration
- **Models**: ML model training and inference
- **Database**: Data persistence and retrieval

**Technology**: FastAPI, SQLAlchemy, scikit-learn

---

### Frontend (`/frontend`)

**Purpose**: User interface and visualization

**Key Components**:
- **Dashboard**: Main application interface
- **Components**: Reusable UI elements
- **API Client**: Backend communication

**Technology**: Streamlit, Plotly, Pandas

---

### Data (`/data`)

**Purpose**: Data generation and management

**Key Components**:
- **Mock Generator**: Simulates real-time manufacturing data
- **Scenarios**: Predefined failure patterns
- **Sample Data**: Training and testing datasets

**Technology**: Python, NumPy, Pandas

---

### ML (`/ml`)

**Purpose**: Machine learning pipeline

**Key Components**:
- **Training**: Model development and training
- **Features**: Feature engineering logic
- **Saved Models**: Trained model artifacts

**Technology**: scikit-learn, TensorFlow (optional)

---

### Orchestrate (`/orchestrate`)

**Purpose**: Workflow automation

**Key Components**:
- **Workflows**: Alert and escalation workflows
- **Skills**: Custom automation skills

**Technology**: IBM watsonx Orchestrate

---

### watsonx (`/watsonx`)

**Purpose**: AI reasoning and NLP

**Key Components**:
- **Prompts**: Prompt engineering templates
- **Config**: API configuration

**Technology**: IBM watsonx.ai

---

### Bob Sessions (`/bob_sessions`)

**Purpose**: Documentation for judging

**Key Components**:
- **Session Reports**: Exported Bob task sessions
- **Screenshots**: Development process evidence

**Technology**: IBM Bob IDE exports

---

## File Naming Conventions

### Python Files
- **Modules**: `lowercase_with_underscores.py`
- **Classes**: `PascalCase` (e.g., `DataProcessor`)
- **Functions**: `snake_case` (e.g., `process_data`)
- **Constants**: `UPPER_CASE` (e.g., `MAX_BATCH_SIZE`)

### Configuration Files
- **Environment**: `.env`, `.env.example`
- **YAML**: `lowercase_config.yaml`
- **JSON**: `lowercase_config.json`

### Documentation
- **Markdown**: `UPPERCASE_TITLE.md`
- **Notebooks**: `lowercase_description.ipynb`

---

## Development Workflow

### 1. Initial Setup
```bash
# Clone repository
git clone <repo-url>
cd packaging-ai-copilot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python scripts/setup_db.py

# Generate sample data
python scripts/generate_sample_data.py
```

### 2. Development
```bash
# Terminal 1: Run backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2: Run frontend
cd frontend
streamlit run dashboard.py --server.port 8501

# Terminal 3: Run mock data generator
cd data/mock
python generator.py
```

### 3. Testing
```bash
# Run backend tests
cd backend
pytest tests/

# Run integration tests
pytest tests/integration/
```

### 4. Deployment
```bash
# Build Docker images
docker-compose build

# Run containers
docker-compose up -d

# Check logs
docker-compose logs -f
```

---

## Configuration Management

### Environment Variables (`.env`)

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/packaging_db

# API
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=True

# watsonx.ai
WATSONX_API_KEY=your_api_key_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_PROJECT_ID=your_project_id

# watsonx Orchestrate
ORCHESTRATE_API_KEY=your_orchestrate_key
ORCHESTRATE_URL=https://orchestrate.ibm.com

# ML Model
MODEL_PATH=ml/saved_models/model_v1.pkl
CONFIDENCE_THRESHOLD=0.75

# Alerts
ALERT_EMAIL=manager@company.com
ALERT_WEBHOOK=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

---

## Git Workflow

### Branch Strategy
- `main`: Production-ready code
- `develop`: Integration branch
- `feature/*`: Feature development
- `bugfix/*`: Bug fixes

### Commit Messages
```
feat: Add real-time data streaming endpoint
fix: Resolve database connection timeout
docs: Update API documentation
refactor: Improve copilot response generation
test: Add unit tests for mapping engine
```

---

## Dependencies Overview

### Backend Dependencies
```
fastapi==0.104.1          # Web framework
uvicorn==0.24.0           # ASGI server
pydantic==2.5.0           # Data validation
sqlalchemy==2.0.23        # ORM
psycopg2-binary==2.9.9    # PostgreSQL driver
scikit-learn==1.3.2       # ML library
pandas==2.1.3             # Data manipulation
numpy==1.26.2             # Numerical computing
python-dotenv==1.0.0      # Environment variables
ibm-watsonx-ai==0.1.0     # watsonx.ai SDK
```

### Frontend Dependencies
```
streamlit==1.28.2         # Dashboard framework
plotly==5.18.0            # Interactive charts
pandas==2.1.3             # Data manipulation
requests==2.31.0          # HTTP client
```

### Development Dependencies
```
pytest==7.4.3             # Testing framework
black==23.11.0            # Code formatter
flake8==6.1.0             # Linter
mypy==1.7.1               # Type checker
```

---

## Next Steps

After reviewing this structure:

1. **Confirm folder structure** meets requirements
2. **Proceed to STEP 2**: Data Schema & Process Intelligence Design
3. **Begin implementation** with mock data generator
4. **Iterate and refine** based on testing

---

**Status**: Architecture and structure defined ✅
**Next**: Data schema design and implementation planning