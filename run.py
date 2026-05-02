"""
Simple run script for AI Packaging Reliability Copilot
Quick start: python run.py
"""

import subprocess
import sys
import os
import time

def print_banner():
    """Print startup banner"""
    print("\n" + "="*80)
    print("AI PACKAGING RELIABILITY COPILOT".center(80))
    print("Powered by IBM Bob | watsonx.ai | watsonx Orchestrate".center(80))
    print("="*80 + "\n")

def check_python():
    """Check Python version"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python 3.8+ required (found {version.major}.{version.minor}.{version.micro})")
        return False

def install_dependencies():
    """Install required packages"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"])
        print("✓ Dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to install dependencies")
        print("  Try manually: pip install -r requirements.txt")
        return False

def init_database():
    """Initialize database"""
    print("\n🗄️  Initializing database...")
    try:
        from backend.app.db.database import engine, Base
        from backend.app.db.models import ProcessData, Prediction, AlertHistory
        Base.metadata.create_all(bind=engine)
        print("✓ Database initialized")
        return True
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False

def start_backend():
    """Start backend server"""
    print("\n🚀 Starting backend server...")
    try:
        backend = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "backend.app.main:app", 
             "--host", "0.0.0.0", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(3)
        print("✓ Backend running at http://localhost:8000")
        return backend
    except Exception as e:
        print(f"✗ Failed to start backend: {e}")
        return None

def start_dashboard():
    """Start dashboard"""
    print("\n🎨 Starting dashboard...")
    try:
        dashboard = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "frontend/dashboard.py",
             "--server.port", "8501", "--server.headless", "true"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(3)
        print("✓ Dashboard running at http://localhost:8501")
        return dashboard
    except Exception as e:
        print(f"✗ Failed to start dashboard: {e}")
        return None

def show_info():
    """Show system information"""
    print("\n" + "="*80)
    print("SYSTEM READY".center(80))
    print("="*80)
    
    print("\n📍 Access Points:")
    print("   Dashboard:  http://localhost:8501")
    print("   Backend:    http://localhost:8000")
    print("   API Docs:   http://localhost:8000/docs")
    
    print("\n🎯 Quick Start:")
    print("   1. Open http://localhost:8501 in your browser")
    print("   2. Click 'Generate New Data' in sidebar")
    print("   3. Click 'Get Prediction' to classify")
    print("   4. Explore different tabs and scenarios")
    
    print("\n💬 Try AI Copilot:")
    print("   • 'Why is this batch severe?'")
    print("   • 'Analyze die attach issue'")
    print("   • 'What parameters are abnormal?'")
    print("   • 'Suggest optimization'")
    
    print("\n⚠️  Press Ctrl+C to stop all services")
    print("="*80 + "\n")

def main():
    """Main entry point"""
    print_banner()
    
    # Check Python version
    if not check_python():
        sys.exit(1)
    
    # Install dependencies
    print("\nChecking dependencies...")
    try:
        import fastapi
        import streamlit
        print("✓ Dependencies already installed")
    except ImportError:
        if not install_dependencies():
            sys.exit(1)
    
    # Initialize database
    if not init_database():
        print("\n⚠️  Continuing without database initialization")
    
    # Start backend
    backend = start_backend()
    if not backend:
        print("\n✗ Failed to start backend")
        sys.exit(1)
    
    # Start dashboard
    dashboard = start_dashboard()
    if not dashboard:
        print("\n✗ Failed to start dashboard")
        if backend:
            backend.terminate()
        sys.exit(1)
    
    # Show info
    show_info()
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        if dashboard:
            dashboard.terminate()
            print("✓ Dashboard stopped")
        if backend:
            backend.terminate()
            print("✓ Backend stopped")
        print("✓ Shutdown complete\n")

if __name__ == "__main__":
    main()

# Made with Bob
