"""
System Startup Script for AI Packaging Reliability Copilot
Initializes all components and starts the complete system
"""

import subprocess
import sys
import os
import time
import requests
from pathlib import Path

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")


def print_step(step_num, text):
    """Print step information"""
    print(f"{Colors.OKCYAN}{Colors.BOLD}[STEP {step_num}]{Colors.ENDC} {text}")


def print_success(text):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_warning(text):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def print_info(text):
    """Print info message"""
    print(f"{Colors.OKBLUE}ℹ {text}{Colors.ENDC}")


def check_python_version():
    """Check Python version"""
    print_step(1, "Checking Python version...")
    
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python 3.8+ required, found {version.major}.{version.minor}.{version.micro}")
        return False


def check_dependencies():
    """Check if required packages are installed"""
    print_step(2, "Checking dependencies...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'streamlit',
        'sqlalchemy',
        'pandas',
        'numpy',
        'scikit-learn',
        'plotly',
        'pydantic'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print_success(f"{package} installed")
        except ImportError:
            missing.append(package)
            print_error(f"{package} not found")
    
    if missing:
        print_warning(f"Missing packages: {', '.join(missing)}")
        print_info("Run: pip install -r requirements.txt")
        return False
    
    return True


def initialize_database():
    """Initialize database"""
    print_step(3, "Initializing database...")
    
    try:
        # Import database setup
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from backend.app.db.database import engine, Base
        from backend.app.db.models import ProcessData, Prediction, AlertHistory
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        print_success("Database tables created")
        return True
    
    except Exception as e:
        print_error(f"Database initialization failed: {e}")
        return False


def train_ml_model():
    """Train ML model if not exists"""
    print_step(4, "Checking ML model...")
    
    model_path = Path("ml/saved_models/packaging_classifier.pkl")
    
    if model_path.exists():
        print_success("ML model found")
        return True
    
    print_info("Training ML model (this may take a minute)...")
    
    try:
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from ml.training.train import train_model
        
        # Train model
        train_model()
        print_success("ML model trained successfully")
        return True
    
    except Exception as e:
        print_error(f"ML model training failed: {e}")
        print_warning("System will use rule-based classification")
        return True  # Continue anyway


def start_backend():
    """Start FastAPI backend server"""
    print_step(5, "Starting backend server...")
    
    try:
        # Start backend in background
        backend_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for backend to start
        print_info("Waiting for backend to start...")
        time.sleep(5)
        
        # Check if backend is running
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print_success("Backend server running at http://localhost:8000")
                return backend_process
            else:
                print_error("Backend health check failed")
                return None
        except requests.exceptions.RequestException:
            print_error("Backend not responding")
            return None
    
    except Exception as e:
        print_error(f"Failed to start backend: {e}")
        return None


def start_dashboard():
    """Start Streamlit dashboard"""
    print_step(6, "Starting dashboard...")
    
    try:
        # Start dashboard
        dashboard_process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "frontend/dashboard.py", "--server.port", "8501"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print_info("Waiting for dashboard to start...")
        time.sleep(5)
        
        print_success("Dashboard running at http://localhost:8501")
        return dashboard_process
    
    except Exception as e:
        print_error(f"Failed to start dashboard: {e}")
        return None


def display_system_info():
    """Display system information"""
    print_header("SYSTEM READY")
    
    print(f"{Colors.BOLD}Access Points:{Colors.ENDC}")
    print(f"  • Dashboard:  {Colors.OKGREEN}http://localhost:8501{Colors.ENDC}")
    print(f"  • Backend API: {Colors.OKGREEN}http://localhost:8000{Colors.ENDC}")
    print(f"  • API Docs:    {Colors.OKGREEN}http://localhost:8000/docs{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}Quick Start:{Colors.ENDC}")
    print("  1. Open dashboard in browser")
    print("  2. Click 'Generate New Data' in sidebar")
    print("  3. Click 'Get Prediction' to classify")
    print("  4. Explore different tabs:")
    print("     - Real-Time: Live parameter monitoring")
    print("     - ML Analysis: Model predictions and explainability")
    print("     - AI Copilot: Natural language interaction")
    print("     - Alerts: Alert management and workflows")
    print("     - Historical: Trend analysis")
    
    print(f"\n{Colors.BOLD}Test Scenarios:{Colors.ENDC}")
    print("  • Normal Operation")
    print("  • Die Attach Issue")
    print("  • Wire Bond Issue")
    print("  • Molding Issue")
    print("  • Curing Issue")
    print("  • Electrical Failure")
    print("  • High Defect Rate")
    print("  • Process Drift")
    
    print(f"\n{Colors.BOLD}AI Copilot Commands:{Colors.ENDC}")
    print("  • 'Why is this batch severe?'")
    print("  • 'Analyze die attach issue'")
    print("  • 'What parameters are abnormal?'")
    print("  • 'Suggest optimization'")
    print("  • 'Explain the current status'")
    
    print(f"\n{Colors.WARNING}Press Ctrl+C to stop all services{Colors.ENDC}\n")


def main():
    """Main startup sequence"""
    
    print_header("AI PACKAGING RELIABILITY COPILOT")
    print_info("Powered by IBM Bob | watsonx.ai | watsonx Orchestrate")
    
    # Step 1: Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Step 2: Check dependencies
    if not check_dependencies():
        print_error("Please install missing dependencies first")
        sys.exit(1)
    
    # Step 3: Initialize database
    if not initialize_database():
        print_error("Database initialization failed")
        sys.exit(1)
    
    # Step 4: Train/check ML model
    train_ml_model()
    
    # Step 5: Start backend
    backend_process = start_backend()
    if not backend_process:
        print_error("Failed to start backend server")
        sys.exit(1)
    
    # Step 6: Start dashboard
    dashboard_process = start_dashboard()
    if not dashboard_process:
        print_error("Failed to start dashboard")
        backend_process.terminate()
        sys.exit(1)
    
    # Display system info
    display_system_info()
    
    # Keep running until interrupted
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Shutting down...{Colors.ENDC}")
        
        # Stop processes
        if dashboard_process:
            dashboard_process.terminate()
            print_success("Dashboard stopped")
        
        if backend_process:
            backend_process.terminate()
            print_success("Backend stopped")
        
        print_success("System shutdown complete")


if __name__ == "__main__":
    main()

# Made with Bob
