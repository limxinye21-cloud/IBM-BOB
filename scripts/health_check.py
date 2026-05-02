"""
System Health Check Script
Verifies all components are functioning correctly
"""

import requests
import sys
import os
from pathlib import Path
import time
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


class HealthChecker:
    """System health checker"""
    
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.dashboard_url = "http://localhost:8501"
        self.results = []
    
    def print_header(self, text):
        """Print section header"""
        print(f"\n{'='*80}")
        print(f"{text.center(80)}")
        print(f"{'='*80}\n")
    
    def print_check(self, name, status, message=""):
        """Print check result"""
        symbol = "✓" if status else "✗"
        color = "\033[92m" if status else "\033[91m"
        reset = "\033[0m"
        
        print(f"{color}{symbol}{reset} {name:<40} {message}")
        self.results.append({'name': name, 'status': status, 'message': message})
    
    def check_backend_health(self):
        """Check backend API health"""
        print("\n[1] Backend API Health")
        print("-" * 80)
        
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                self.print_check("Backend API", True, "Running")
                
                # Check components
                if 'database' in data:
                    db_status = data['database'] == 'connected'
                    self.print_check("Database Connection", db_status, 
                                   data.get('database', 'unknown'))
                
                if 'ml_model' in data:
                    ml_status = data['ml_model'] == 'loaded'
                    self.print_check("ML Model", ml_status, 
                                   data.get('ml_model', 'unknown'))
                
                return True
            else:
                self.print_check("Backend API", False, f"Status: {response.status_code}")
                return False
        
        except requests.exceptions.ConnectionError:
            self.print_check("Backend API", False, "Not responding")
            return False
        except Exception as e:
            self.print_check("Backend API", False, str(e))
            return False
    
    def check_dashboard_health(self):
        """Check dashboard health"""
        print("\n[2] Dashboard Health")
        print("-" * 80)
        
        try:
            response = requests.get(self.dashboard_url, timeout=5)
            
            if response.status_code == 200:
                self.print_check("Dashboard", True, "Running")
                return True
            else:
                self.print_check("Dashboard", False, f"Status: {response.status_code}")
                return False
        
        except requests.exceptions.ConnectionError:
            self.print_check("Dashboard", False, "Not responding")
            return False
        except Exception as e:
            self.print_check("Dashboard", False, str(e))
            return False
    
    def check_api_endpoints(self):
        """Check critical API endpoints"""
        print("\n[3] API Endpoints")
        print("-" * 80)
        
        endpoints = [
            ("/health", "GET", "Health Check"),
            ("/data/latest", "GET", "Latest Data"),
            ("/ml/status", "GET", "ML Status"),
            ("/copilot/health", "GET", "Copilot Health"),
            ("/alerts/active", "GET", "Active Alerts"),
        ]
        
        for endpoint, method, name in endpoints:
            try:
                url = f"{self.backend_url}{endpoint}"
                
                if method == "GET":
                    response = requests.get(url, timeout=5)
                else:
                    response = requests.post(url, json={}, timeout=5)
                
                if response.status_code in [200, 404]:  # 404 is ok for empty data
                    self.print_check(name, True, f"{method} {endpoint}")
                else:
                    self.print_check(name, False, f"Status: {response.status_code}")
            
            except Exception as e:
                self.print_check(name, False, str(e))
    
    def check_database(self):
        """Check database connectivity and tables"""
        print("\n[4] Database")
        print("-" * 80)
        
        try:
            from backend.app.db.database import engine, SessionLocal
            from backend.app.db.models import ProcessData, Prediction, AlertHistory
            
            # Test connection
            with engine.connect() as conn:
                self.print_check("Database Connection", True, "Connected")
            
            # Check tables
            tables = ['process_data', 'predictions', 'alert_history']
            for table in tables:
                try:
                    with engine.connect() as conn:
                        result = conn.execute(f"SELECT COUNT(*) FROM {table}")
                        count = result.scalar()
                        self.print_check(f"Table: {table}", True, f"{count} records")
                except Exception as e:
                    self.print_check(f"Table: {table}", False, str(e))
        
        except Exception as e:
            self.print_check("Database", False, str(e))
    
    def check_ml_model(self):
        """Check ML model"""
        print("\n[5] ML Model")
        print("-" * 80)
        
        model_path = Path("ml/saved_models/packaging_classifier.pkl")
        
        if model_path.exists():
            self.print_check("Model File", True, str(model_path))
            
            # Try loading model
            try:
                import joblib
                model = joblib.load(model_path)
                self.print_check("Model Loading", True, type(model).__name__)
                
                # Check model attributes
                if hasattr(model, 'n_features_in_'):
                    self.print_check("Model Features", True, 
                                   f"{model.n_features_in_} features")
            
            except Exception as e:
                self.print_check("Model Loading", False, str(e))
        else:
            self.print_check("Model File", False, "Not found")
    
    def check_data_generator(self):
        """Check mock data generator"""
        print("\n[6] Data Generator")
        print("-" * 80)
        
        try:
            from data.mock.generator import MockDataGenerator
            from data.mock.scenarios import SCENARIOS
            
            generator = MockDataGenerator()
            self.print_check("Generator Import", True, "MockDataGenerator")
            
            # Test data generation
            data = generator.generate_single()
            if data and 'batch_id' in data:
                self.print_check("Data Generation", True, f"Batch: {data['batch_id']}")
            else:
                self.print_check("Data Generation", False, "Invalid data")
            
            # Check scenarios
            self.print_check("Scenarios", True, f"{len(SCENARIOS)} scenarios")
        
        except Exception as e:
            self.print_check("Data Generator", False, str(e))
    
    def check_dependencies(self):
        """Check required Python packages"""
        print("\n[7] Dependencies")
        print("-" * 80)
        
        required = [
            'fastapi',
            'uvicorn',
            'streamlit',
            'sqlalchemy',
            'pandas',
            'numpy',
            'scikit-learn',
            'plotly',
            'pydantic',
            'requests'
        ]
        
        for package in required:
            try:
                __import__(package)
                self.print_check(package, True, "Installed")
            except ImportError:
                self.print_check(package, False, "Not installed")
    
    def check_file_structure(self):
        """Check critical files and directories"""
        print("\n[8] File Structure")
        print("-" * 80)
        
        critical_paths = [
            "backend/app/main.py",
            "frontend/dashboard.py",
            "data/mock/generator.py",
            "ml/training/train.py",
            "requirements.txt",
            "README.md"
        ]
        
        for path in critical_paths:
            exists = Path(path).exists()
            self.print_check(path, exists, "Found" if exists else "Missing")
    
    def test_end_to_end(self):
        """Test end-to-end workflow"""
        print("\n[9] End-to-End Test")
        print("-" * 80)
        
        try:
            # Generate data
            from data.mock.generator import MockDataGenerator
            generator = MockDataGenerator()
            data = generator.generate_single()
            self.print_check("Generate Data", True, "Success")
            
            # Send to API
            response = requests.post(
                f"{self.backend_url}/data/ingest",
                json=data,
                timeout=5
            )
            
            if response.status_code == 200:
                self.print_check("Data Ingestion", True, "Success")
            else:
                self.print_check("Data Ingestion", False, f"Status: {response.status_code}")
            
            # Get prediction
            response = requests.post(
                f"{self.backend_url}/ml/predict",
                json=data,
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                status = result.get('prediction', {}).get('status', 'UNKNOWN')
                self.print_check("ML Prediction", True, f"Status: {status}")
            else:
                self.print_check("ML Prediction", False, f"Status: {response.status_code}")
        
        except Exception as e:
            self.print_check("End-to-End Test", False, str(e))
    
    def generate_report(self):
        """Generate health check report"""
        print("\n" + "="*80)
        print("HEALTH CHECK SUMMARY".center(80))
        print("="*80 + "\n")
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r['status'])
        failed = total - passed
        
        print(f"Total Checks: {total}")
        print(f"Passed: {passed} (\033[92m{passed/total*100:.1f}%\033[0m)")
        print(f"Failed: {failed} (\033[91m{failed/total*100:.1f}%\033[0m)")
        
        if failed > 0:
            print(f"\n\033[91mFailed Checks:\033[0m")
            for result in self.results:
                if not result['status']:
                    print(f"  ✗ {result['name']}: {result['message']}")
        
        print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80 + "\n")
        
        return failed == 0
    
    def run_all_checks(self):
        """Run all health checks"""
        self.print_header("AI PACKAGING RELIABILITY COPILOT - HEALTH CHECK")
        
        # Run checks
        self.check_backend_health()
        self.check_dashboard_health()
        self.check_api_endpoints()
        self.check_database()
        self.check_ml_model()
        self.check_data_generator()
        self.check_dependencies()
        self.check_file_structure()
        self.test_end_to_end()
        
        # Generate report
        success = self.generate_report()
        
        return 0 if success else 1


def main():
    """Main entry point"""
    checker = HealthChecker()
    exit_code = checker.run_all_checks()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

# Made with Bob
