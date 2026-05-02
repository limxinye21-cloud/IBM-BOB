# Quick Start Guide - AI Packaging Reliability Copilot

## 🚀 Get Started in 5 Minutes

This guide will help you run the system and see it in action immediately.

---

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

---

## Step 1: Install Dependencies

Open terminal in the project directory and run:

```bash
pip install -r requirements.txt
```

**Required packages:**
- fastapi
- uvicorn
- streamlit
- sqlalchemy
- pandas
- numpy
- scikit-learn
- plotly
- pydantic
- requests

---

## Step 2: Initialize Database

```bash
python -c "from backend.app.db.database import engine, Base; from backend.app.db.models import ProcessData, Prediction, AlertHistory; Base.metadata.create_all(bind=engine); print('✓ Database initialized')"
```

---

## Step 3: Start the System

### Option A: Automated Startup (Recommended)

```bash
python scripts/start_system.py
```

This will:
- Check all dependencies
- Initialize database
- Start backend API
- Start dashboard
- Display access URLs

### Option B: Manual Startup

**Terminal 1 - Start Backend:**
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Start Dashboard:**
```bash
streamlit run frontend/dashboard.py --server.port 8501
```

---

## Step 4: Access the System

Once started, open your browser:

- **Dashboard**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health

---

## Step 5: Try It Out!

### 5.1 Generate Data

1. In the dashboard sidebar, click **"🔄 Generate New Data"**
2. Select a scenario (try "Die Attach Issue" for demo)
3. Watch the data appear in the main panel

### 5.2 Get ML Prediction

1. Click **"📈 Get Prediction"** in sidebar
2. See the status classification (GOOD/WARNING/SEVERE)
3. View confidence score

### 5.3 Explore Tabs

**📈 Real-Time Parameters:**
- View live parameter gauges
- See die attach, wire bonding, molding, curing metrics

**🤖 ML Analysis:**
- View prediction probabilities
- See feature importance
- Analyze critical parameters

**💬 AI Copilot:**
- Ask questions like:
  - "Why is this batch severe?"
  - "Analyze die attach issue"
  - "What parameters are abnormal?"
  - "Suggest optimization"
- Get AI-powered explanations

**🚨 Alerts:**
- View active alerts
- See alert statistics
- Manage alert lifecycle

**📊 Historical Trends:**
- View historical data
- Analyze trends
- See status distribution

---

## Quick Demo Scenarios

### Scenario 1: Normal Operation

```
1. Select "Normal" scenario
2. Generate data
3. Get prediction → Should show GOOD status
4. No alerts should trigger
```

### Scenario 2: Severe Condition

```
1. Select "Die Attach Issue" scenario
2. Generate data
3. Get prediction → Should show SEVERE status
4. Check Alerts tab → Should see critical alert
5. Ask Copilot: "Why is this batch severe?"
```

### Scenario 3: AI Copilot Interaction

```
1. Generate any data
2. Go to AI Copilot tab
3. Try these queries:
   - "Analyze die attach issue"
   - "What parameters are abnormal?"
   - "Suggest optimization"
4. See intelligent responses
```

---

## Testing the API

### Using curl:

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Generate and Ingest Data:**
```bash
curl -X POST http://localhost:8000/data/ingest \
  -H "Content-Type: application/json" \
  -d @sample_data.json
```

**Get Prediction:**
```bash
curl -X POST http://localhost:8000/ml/predict \
  -H "Content-Type: application/json" \
  -d @sample_data.json
```

**Check Alerts:**
```bash
curl http://localhost:8000/alerts/active
```

### Using Python:

```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())

# Get latest data
response = requests.get("http://localhost:8000/data/latest?limit=5")
print(response.json())

# Get active alerts
response = requests.get("http://localhost:8000/alerts/active")
print(response.json())
```

---

## Verify System Health

Run the health check script:

```bash
python scripts/health_check.py
```

This will verify:
- ✓ Backend API running
- ✓ Dashboard accessible
- ✓ Database connected
- ✓ ML model loaded
- ✓ All endpoints working
- ✓ Dependencies installed

---

## Common Issues & Solutions

### Issue 1: Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:8000 | xargs kill -9
```

### Issue 2: Module Not Found

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue 3: Database Error

**Error:** `OperationalError: no such table`

**Solution:**
```bash
# Reinitialize database
python -c "from backend.app.db.database import engine, Base; Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine)"
```

### Issue 4: Dashboard Not Loading

**Error:** Dashboard shows blank page

**Solution:**
```bash
# Clear Streamlit cache
rm -rf ~/.streamlit/cache

# Restart dashboard
streamlit run frontend/dashboard.py --server.port 8501
```

---

## What to Look For

### ✅ System is Working When:

1. **Backend API:**
   - Health endpoint returns 200 OK
   - API docs accessible at /docs
   - No error messages in terminal

2. **Dashboard:**
   - Loads without errors
   - Sidebar shows "✓ Backend Connected"
   - Can generate data successfully

3. **ML Model:**
   - Predictions return status (GOOD/WARNING/SEVERE)
   - Confidence scores displayed
   - Feature importance shown

4. **Alerts:**
   - Alerts trigger for severe conditions
   - Alert panel shows active alerts
   - Statistics display correctly

5. **AI Copilot:**
   - Responds to queries
   - Provides explanations
   - Suggests recommendations

---

## Next Steps

Once the system is running:

1. **Explore All Scenarios:**
   - Try all 8 predefined scenarios
   - See how different issues are detected

2. **Test AI Copilot:**
   - Ask various questions
   - See how it analyzes different issues

3. **Check Alert System:**
   - Trigger severe conditions
   - See alert notifications
   - Test workflow creation

4. **Review Documentation:**
   - Read SYSTEM_ARCHITECTURE.md
   - Check API_DOCUMENTATION.md
   - Review DEPLOYMENT_GUIDE.md

---

## Demo Tips for Hackathon

### What to Show Judges:

1. **System Startup** (30 seconds)
   - Run `python scripts/start_system.py`
   - Show clean startup sequence

2. **Real-Time Monitoring** (1 minute)
   - Generate data with different scenarios
   - Show parameter gauges updating
   - Display status light changes

3. **ML Classification** (1 minute)
   - Show prediction for normal data
   - Show prediction for severe data
   - Explain confidence scores

4. **AI Copilot** (2 minutes)
   - Ask "Why is this batch severe?"
   - Show root cause analysis
   - Display recommendations
   - Highlight natural language understanding

5. **Alert System** (1 minute)
   - Show alert triggering
   - Display alert details
   - Demonstrate workflow creation

6. **watsonx Integration** (1 minute)
   - Explain watsonx.ai usage
   - Show watsonx Orchestrate workflows
   - Highlight automation capabilities

### Key Talking Points:

- **IBM Bob Usage:** "We used IBM Bob to design, generate, and integrate all components"
- **Production-Ready:** "19,000+ lines of production-grade code"
- **Real-World Impact:** "Reduces issue detection time from hours to seconds"
- **Scalable Architecture:** "Ready for deployment in real manufacturing"

---

## Support

If you encounter issues:

1. Check `scripts/health_check.py` output
2. Review terminal logs for errors
3. Verify all dependencies installed
4. Ensure ports 8000 and 8501 are available

---

## Summary

```bash
# Quick start commands:
pip install -r requirements.txt
python scripts/start_system.py

# Access:
# Dashboard: http://localhost:8501
# API: http://localhost:8000/docs
```

**You're ready to go! 🚀**

Generate data, get predictions, ask the AI Copilot questions, and explore the system!