# Dashboard Quick Start Guide

## AI Packaging Reliability Copilot - Dashboard

This guide will help you quickly set up and run the Streamlit dashboard.

---

## Prerequisites

- Python 3.9 or higher
- Backend API running (see Backend Setup below)
- All dependencies installed

---

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Key packages for dashboard:
- `streamlit==1.28.2` - Dashboard framework
- `plotly==5.18.0` - Interactive charts
- `requests==2.31.0` - API communication
- `pandas==2.1.3` - Data handling

### 2. Verify Installation

```bash
streamlit --version
# Should show: Streamlit, version 1.28.2
```

---

## Running the System

### Step 1: Start Backend API

Open a terminal and run:

```bash
# From project root
python backend/app/main.py
```

Expected output:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

Verify backend is running:
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy",...}
```

### Step 2: Start Dashboard

Open a **new terminal** and run:

```bash
# From project root
streamlit run frontend/dashboard.py
```

Expected output:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### Step 3: Access Dashboard

Open your browser and navigate to:
```
http://localhost:8501
```

---

## Dashboard Overview

### Sidebar (Left Panel)

**System Status**:
- ✓ Backend Connected (green) - API is reachable
- ✓ ML Model Loaded (green) - Model ready for predictions
- ⚠ ML Model Not Available (yellow) - Using rule-based fallback
- ✗ Backend Disconnected (red) - Start backend first

**Data Source**:
- **Mock Generator**: Simulated manufacturing data
- **Manual Input**: Enter parameters manually
- **Live API**: Fetch from backend database

**Scenario Selection** (Mock Generator only):
- Normal - Standard operation
- Die Attach Drift - Temperature instability
- Wire Bonding Failure - Low pull strength
- Molding Issue - High void percentage
- Curing Incomplete - Poor uniformity
- Inspection Failure - High defect count
- Cascading Failure - Multi-stage issues
- Intermittent Warnings - Fluctuating parameters

**Auto-Refresh**:
- Enable checkbox for automatic updates
- Adjust interval (1-10 seconds)

**Action Buttons**:
- 🔄 Generate New Data - Create new process data
- 📈 Get Prediction - Run ML classification
- 🧹 Clear History - Reset prediction timeline

### Main Content (5 Tabs)

#### Tab 1: 📈 Real-Time Parameters

**Status Light**:
- Large animated circle showing current status
- 🟢 GOOD - All parameters normal
- 🟡 WARNING - Some parameters outside range
- 🔴 SEVERE - Critical issues detected

**Key Metrics** (4 cards):
- Batch ID
- Reliability Score
- Defect Count
- Void Percentage

**Process Stage Overview**:
- 5 stages with health indicators
- ✓ = Good, ⚠ = Warning

**Parameter Gauges** (9 gauges):
- Die Attach: Temperature, Void %, Placement Accuracy
- Wire Bonding: Bonding Force, Pull Strength, Loop Height
- Molding & Curing: Mold Temp, Cure Uniformity, Mold Voids

#### Tab 2: 🤖 ML Analysis

**Prediction Probabilities**:
- Progress bars for GOOD/WARNING/SEVERE
- Shows confidence for each status

**Status History**:
- Donut chart of status distribution
- Visual breakdown of predictions

**Explain Prediction Button**:
- Click to analyze feature importance
- Shows top 10 contributing features
- Identifies critical parameters

**Critical Parameters**:
- Lists parameters needing attention
- Shows current value and importance

#### Tab 3: 📊 Historical Trends

**Prediction Timeline**:
- Last 10 predictions with timestamps
- Color-coded by status
- Shows confidence scores

**Confidence Distribution**:
- Histogram of prediction confidence
- Helps assess model reliability

#### Tab 4: ⚙️ Manual Input

**Parameter Entry Form**:
- Die Attach: Temperature, Void %, Placement
- Wire Bonding: Force, Pull Strength, Loop Height
- Molding: Temperature, Voids
- Curing: Temperature, Uniformity
- Inspection: Reliability Score, Defect Count

**Submit Button**:
- Creates complete data record
- Auto-fills remaining parameters
- Returns to main view

#### Tab 5: 📋 Data Details

**Complete Data Table**:
- All 33 process parameters
- Scrollable view
- Current values

**Download Button**:
- Export data to CSV
- Timestamped filename

---

## Basic Workflow

### Scenario 1: Normal Operation Monitoring

1. **Check System Status** (sidebar)
   - Verify green checkmarks

2. **Select Mock Generator** (sidebar)
   - Choose "Normal" scenario

3. **Generate Data** (sidebar)
   - Click "🔄 Generate New Data"
   - Status light appears

4. **Get Prediction** (sidebar)
   - Click "📈 Get Prediction"
   - View confidence score

5. **Review Parameters** (Tab 1)
   - Check all gauges are green
   - Verify key metrics

### Scenario 2: Failure Analysis

1. **Select Failure Scenario** (sidebar)
   - Choose "Wire Bonding Failure"

2. **Generate Data** (sidebar)
   - Click "🔄 Generate New Data"
   - Status light shows SEVERE (red)

3. **Get Prediction** (sidebar)
   - Click "📈 Get Prediction"
   - Note high SEVERE probability

4. **Analyze Root Cause** (Tab 2)
   - Click "🧠 Explain Prediction"
   - Review feature importance chart
   - Identify critical parameters
   - Example: "wire_pull_strength" shows low value

5. **Review History** (Tab 3)
   - Check prediction timeline
   - Analyze confidence distribution

### Scenario 3: Manual Testing

1. **Go to Manual Input** (Tab 4)

2. **Enter Custom Values**:
   - Die Temperature: 195°C (high)
   - Void %: 6% (high)
   - Pull Strength: 5gf (low)

3. **Submit Form**
   - Click "Submit Data"

4. **Get Prediction** (sidebar)
   - Click "📈 Get Prediction"
   - Likely shows SEVERE

5. **Analyze Results** (Tab 2)
   - Explain prediction
   - Identify which parameters caused SEVERE

---

## Troubleshooting

### Dashboard Won't Start

**Error**: `ModuleNotFoundError: No module named 'streamlit'`

**Solution**:
```bash
pip install streamlit plotly requests pandas
```

### Backend Connection Failed

**Error**: "✗ Backend Disconnected" in sidebar

**Solution**:
1. Check if backend is running:
   ```bash
   curl http://localhost:8000/health
   ```

2. If not running, start backend:
   ```bash
   python backend/app/main.py
   ```

3. Refresh dashboard (F5)

### ML Model Not Available

**Warning**: "⚠ ML Model Not Available"

**Solution**:
1. Train ML model first:
   ```bash
   python ml/training/train.py
   ```

2. Restart backend:
   ```bash
   # Stop backend (Ctrl+C)
   python backend/app/main.py
   ```

3. Refresh dashboard

**Note**: Dashboard will work with rule-based classification if ML model unavailable.

### Port Already in Use

**Error**: `OSError: [Errno 48] Address already in use`

**Solution**:
```bash
# Kill process on port 8501
lsof -ti:8501 | xargs kill -9

# Or use different port
streamlit run frontend/dashboard.py --server.port 8502
```

### Charts Not Displaying

**Issue**: Blank chart areas

**Solution**:
1. Check browser console for errors (F12)
2. Ensure Plotly installed:
   ```bash
   pip install plotly
   ```
3. Clear browser cache
4. Refresh dashboard (F5)

---

## Advanced Features

### Auto-Refresh Mode

Enable continuous monitoring:

1. Check "Enable auto-refresh" (sidebar)
2. Set interval (e.g., 3 seconds)
3. Dashboard auto-generates data and predictions
4. Useful for demonstrations

### CSV Export

Export current data:

1. Go to "📋 Data Details" tab
2. Click "📥 Download Data (CSV)"
3. File saved with timestamp

### Multiple Scenarios

Test different failure modes:

1. Select scenario from dropdown
2. Generate data
3. Get prediction
4. Compare results across scenarios

---

## Performance Tips

### For Smooth Operation:

1. **Close unused tabs**: Keep only dashboard tab open
2. **Disable auto-refresh**: When not needed
3. **Clear history**: Click "🧹 Clear History" periodically
4. **Use smaller intervals**: 3-5 seconds for auto-refresh

### For Demonstrations:

1. **Enable auto-refresh**: Set to 3 seconds
2. **Use interesting scenarios**: "Cascading Failure" shows multiple issues
3. **Explain predictions**: Show feature importance
4. **Review timeline**: Demonstrate history tracking

---

## Keyboard Shortcuts

- **R**: Rerun dashboard
- **C**: Clear cache
- **F5**: Refresh page
- **Ctrl+C**: Stop dashboard (in terminal)

---

## Next Steps

After familiarizing yourself with the dashboard:

1. **Explore all scenarios**: Understand different failure modes
2. **Test manual input**: Enter edge cases
3. **Review ML explanations**: Learn feature importance
4. **Analyze trends**: Use historical data

---

## Support

For issues or questions:

1. Check `STEP6_SUMMARY.md` for detailed documentation
2. Review `README.md` for project overview
3. Check backend logs for API errors
4. Verify all dependencies installed

---

## Quick Reference

### Start Commands:
```bash
# Backend
python backend/app/main.py

# Dashboard
streamlit run frontend/dashboard.py
```

### URLs:
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Dashboard: http://localhost:8501

### Key Files:
- Dashboard: `frontend/dashboard.py`
- API Client: `frontend/utils/api_client.py`
- Components: `frontend/components/`

---

*Happy Monitoring! 🚀*