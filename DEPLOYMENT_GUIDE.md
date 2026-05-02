# Deployment Guide - AI Packaging Reliability Copilot

## Overview

This guide provides step-by-step instructions for deploying the AI Packaging Reliability Copilot system in different environments.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Production Deployment](#production-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Cloud Deployment (IBM Cloud)](#cloud-deployment-ibm-cloud)
6. [Configuration](#configuration)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Python**: 3.8 or higher
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Disk Space**: 2GB free space
- **Network**: Internet connection for package installation

### Required Software

- Python 3.8+
- pip (Python package manager)
- Git (for cloning repository)
- PostgreSQL 12+ (for production) or SQLite (for development)

---

## Local Development Setup

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd packaging-ai-copilot
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Initialize Database

```bash
python scripts/init_database.py
```

### Step 5: Train ML Model (Optional)

```bash
python ml/training/train.py
```

### Step 6: Start System

**Option A: Automated Startup**
```bash
python scripts/start_system.py
```

**Option B: Manual Startup**

Terminal 1 - Backend:
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 - Dashboard:
```bash
streamlit run frontend/dashboard.py --server.port 8501
```

### Step 7: Access System

- **Dashboard**: http://localhost:8501
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## Production Deployment

### Architecture

```
Load Balancer
    ↓
[Frontend] → [Backend API] → [Database]
                ↓
         [ML Service]
                ↓
         [Alert Service]
```

### Step 1: Environment Setup

Create `.env` file:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/packaging_db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Security
SECRET_KEY=your-secret-key-here
API_KEY=your-api-key-here

# watsonx Configuration
WATSONX_API_KEY=your-watsonx-api-key
WATSONX_PROJECT_ID=your-project-id
WATSONX_ORCHESTRATE_URL=https://orchestrate.watsonx.ibm.com

# Alert Configuration
EMAIL_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@company.com
SMTP_PASSWORD=your-password

SMS_ENABLED=true
SMS_API_KEY=your-sms-api-key

SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/packaging-copilot/app.log
```

### Step 2: Database Setup

```bash
# Create PostgreSQL database
createdb packaging_db

# Run migrations
python scripts/migrate_database.py

# Create indexes
python scripts/create_indexes.py
```

### Step 3: Configure Systemd Services

**Backend Service** (`/etc/systemd/system/packaging-backend.service`):

```ini
[Unit]
Description=AI Packaging Copilot Backend
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/packaging-copilot
Environment="PATH=/opt/packaging-copilot/venv/bin"
ExecStart=/opt/packaging-copilot/venv/bin/uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Dashboard Service** (`/etc/systemd/system/packaging-dashboard.service`):

```ini
[Unit]
Description=AI Packaging Copilot Dashboard
After=network.target packaging-backend.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/packaging-copilot
Environment="PATH=/opt/packaging-copilot/venv/bin"
ExecStart=/opt/packaging-copilot/venv/bin/streamlit run frontend/dashboard.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Step 4: Start Services

```bash
sudo systemctl daemon-reload
sudo systemctl enable packaging-backend
sudo systemctl enable packaging-dashboard
sudo systemctl start packaging-backend
sudo systemctl start packaging-dashboard
```

### Step 5: Configure Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/packaging-copilot

upstream backend {
    server 127.0.0.1:8000;
}

upstream dashboard {
    server 127.0.0.1:8501;
}

server {
    listen 80;
    server_name your-domain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/ssl/certs/your-cert.pem;
    ssl_certificate_key /etc/ssl/private/your-key.pem;

    # Dashboard
    location / {
        proxy_pass http://dashboard;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Docker Deployment

### Dockerfile (Backend)

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/ ./backend/
COPY ml/ ./ml/
COPY data/ ./data/

# Expose port
EXPOSE 8000

# Start application
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Dockerfile (Dashboard)

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY frontend/ ./frontend/
COPY backend/app/utils/ ./backend/app/utils/

# Expose port
EXPOSE 8501

# Start application
CMD ["streamlit", "run", "frontend/dashboard.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  database:
    image: postgres:14
    environment:
      POSTGRES_DB: packaging_db
      POSTGRES_USER: packaging_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build:
      context: .
      dockerfile: docker/Dockerfile.backend
    environment:
      DATABASE_URL: postgresql://packaging_user:secure_password@database:5432/packaging_db
      WATSONX_API_KEY: ${WATSONX_API_KEY}
    ports:
      - "8000:8000"
    depends_on:
      - database
    restart: unless-stopped

  dashboard:
    build:
      context: .
      dockerfile: docker/Dockerfile.dashboard
    environment:
      BACKEND_URL: http://backend:8000
    ports:
      - "8501:8501"
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  postgres_data:
```

### Deploy with Docker Compose

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## Cloud Deployment (IBM Cloud)

### Step 1: Install IBM Cloud CLI

```bash
curl -fsSL https://clis.cloud.ibm.com/install/linux | sh
ibmcloud login
```

### Step 2: Create Cloud Foundry App

```bash
# Create manifest.yml
cat > manifest.yml << EOF
applications:
- name: packaging-copilot-backend
  memory: 1G
  instances: 2
  buildpack: python_buildpack
  command: uvicorn backend.app.main:app --host 0.0.0.0 --port 8080
  env:
    PYTHONUNBUFFERED: true

- name: packaging-copilot-dashboard
  memory: 512M
  instances: 1
  buildpack: python_buildpack
  command: streamlit run frontend/dashboard.py --server.port 8080
EOF

# Deploy
ibmcloud cf push
```

### Step 3: Configure watsonx Integration

```bash
# Create watsonx.ai instance
ibmcloud resource service-instance-create packaging-watsonx watsonxai standard us-south

# Get API key
ibmcloud resource service-key-create packaging-watsonx-key Manager --instance-name packaging-watsonx

# Set environment variables
ibmcloud cf set-env packaging-copilot-backend WATSONX_API_KEY <your-api-key>
```

---

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | Database connection string | `sqlite:///./packaging.db` | No |
| `API_HOST` | API host address | `0.0.0.0` | No |
| `API_PORT` | API port | `8000` | No |
| `SECRET_KEY` | Security secret key | - | Yes (production) |
| `WATSONX_API_KEY` | watsonx.ai API key | - | Yes |
| `WATSONX_PROJECT_ID` | watsonx.ai project ID | - | Yes |
| `EMAIL_ENABLED` | Enable email notifications | `false` | No |
| `SMS_ENABLED` | Enable SMS notifications | `false` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |

### Application Configuration

Edit `backend/app/config.py`:

```python
class Settings:
    # API Configuration
    API_TITLE = "AI Packaging Reliability Copilot"
    API_VERSION = "1.0.0"
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./packaging.db")
    
    # ML Model
    MODEL_PATH = "ml/saved_models/packaging_classifier.pkl"
    
    # Alert Thresholds
    SEVERE_THRESHOLD = 0.7
    WARNING_THRESHOLD = 0.5
    
    # Notification Settings
    EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
    SMS_ENABLED = os.getenv("SMS_ENABLED", "false").lower() == "true"
```

---

## Monitoring & Maintenance

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Database health
curl http://localhost:8000/health/database

# ML model health
curl http://localhost:8000/health/ml
```

### Logging

Logs are stored in:
- Backend: `/var/log/packaging-copilot/backend.log`
- Dashboard: `/var/log/packaging-copilot/dashboard.log`
- Alerts: `/var/log/packaging-copilot/alerts.log`

View logs:
```bash
tail -f /var/log/packaging-copilot/backend.log
```

### Performance Monitoring

```bash
# System metrics
python scripts/system_metrics.py

# API performance
python scripts/api_benchmark.py

# Database performance
python scripts/db_performance.py
```

### Backup & Recovery

```bash
# Backup database
pg_dump packaging_db > backup_$(date +%Y%m%d).sql

# Backup ML model
cp ml/saved_models/packaging_classifier.pkl backups/

# Restore database
psql packaging_db < backup_20240115.sql
```

---

## Troubleshooting

### Common Issues

#### 1. Backend Not Starting

**Symptom**: Backend fails to start or crashes immediately

**Solutions**:
```bash
# Check Python version
python --version  # Should be 3.8+

# Check dependencies
pip list

# Check database connection
python -c "from backend.app.db.database import engine; print(engine)"

# Check logs
tail -f /var/log/packaging-copilot/backend.log
```

#### 2. Dashboard Not Loading

**Symptom**: Dashboard shows blank page or connection error

**Solutions**:
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check Streamlit logs
streamlit run frontend/dashboard.py --logger.level=debug

# Clear Streamlit cache
rm -rf ~/.streamlit/cache
```

#### 3. ML Model Not Loading

**Symptom**: Predictions fail or use rule-based classification

**Solutions**:
```bash
# Retrain model
python ml/training/train.py

# Check model file
ls -lh ml/saved_models/packaging_classifier.pkl

# Test model loading
python -c "import joblib; model = joblib.load('ml/saved_models/packaging_classifier.pkl'); print(model)"
```

#### 4. Database Connection Errors

**Symptom**: "Connection refused" or "Database not found"

**Solutions**:
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection string
echo $DATABASE_URL

# Test connection
psql -h localhost -U packaging_user -d packaging_db
```

#### 5. Alert Notifications Not Sending

**Symptom**: Alerts triggered but notifications not received

**Solutions**:
```bash
# Check environment variables
echo $EMAIL_ENABLED
echo $SMTP_HOST

# Test email configuration
python scripts/test_email.py

# Check alert logs
tail -f /var/log/packaging-copilot/alerts.log
```

### Performance Issues

#### High CPU Usage

```bash
# Check process usage
top -p $(pgrep -f uvicorn)

# Reduce workers
# Edit: uvicorn ... --workers 2

# Enable caching
# Edit backend/app/config.py: ENABLE_CACHE = True
```

#### High Memory Usage

```bash
# Check memory
free -h

# Reduce batch size
# Edit: BATCH_SIZE = 100

# Clear old data
python scripts/cleanup_old_data.py --days 30
```

#### Slow Queries

```bash
# Analyze slow queries
python scripts/analyze_slow_queries.py

# Create indexes
python scripts/create_indexes.py

# Optimize database
VACUUM ANALYZE;
```

---

## Support

For issues and questions:

- **Documentation**: See README.md and other guides
- **GitHub Issues**: <repository-url>/issues
- **Email**: support@company.com
- **Slack**: #packaging-copilot

---

## Appendix

### A. System Requirements by Environment

| Environment | CPU | RAM | Disk | Network |
|-------------|-----|-----|------|---------|
| Development | 2 cores | 4GB | 10GB | 10 Mbps |
| Staging | 4 cores | 8GB | 50GB | 100 Mbps |
| Production | 8 cores | 16GB | 200GB | 1 Gbps |

### B. Port Usage

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| Backend API | 8000 | HTTP | REST API |
| Dashboard | 8501 | HTTP | Web UI |
| PostgreSQL | 5432 | TCP | Database |
| Redis (optional) | 6379 | TCP | Caching |

### C. Security Checklist

- [ ] Change default passwords
- [ ] Enable HTTPS/TLS
- [ ] Configure firewall rules
- [ ] Set up API authentication
- [ ] Enable audit logging
- [ ] Regular security updates
- [ ] Backup encryption
- [ ] Access control (RBAC)

---

**Last Updated**: 2024-01-15
**Version**: 1.0.0