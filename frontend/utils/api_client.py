"""
API Client for AI Packaging Reliability Copilot Dashboard
"""

import requests
from typing import Dict, List, Optional
import streamlit as st


class APIClient:
    """
    Client for interacting with backend API
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize API client
        
        Args:
            base_url: Base URL of the backend API
        """
        self.base_url = base_url
        self.api_prefix = "/api/v1"
        
    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make GET request
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            Response data
        """
        url = f"{self.base_url}{self.api_prefix}{endpoint}"
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"API Error: {e}")
            return {"success": False, "error": str(e)}
    
    def _post(self, endpoint: str, data: Dict) -> Dict:
        """
        Make POST request
        
        Args:
            endpoint: API endpoint
            data: Request body
            
        Returns:
            Response data
        """
        url = f"{self.base_url}{self.api_prefix}{endpoint}"
        try:
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_detail = f"HTTP {e.response.status_code}: {e.response.text if hasattr(e.response, 'text') else str(e)}"
            st.error(f"API Error: {error_detail}")
            return {"success": False, "error": error_detail}
        except requests.exceptions.RequestException as e:
            st.error(f"API Error: {e}")
            return {"success": False, "error": str(e)}
    
    def _delete(self, endpoint: str) -> Dict:
        """
        Make DELETE request
        
        Args:
            endpoint: API endpoint
            
        Returns:
            Response data
        """
        url = f"{self.base_url}{self.api_prefix}{endpoint}"
        try:
            response = requests.delete(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"API Error: {e}")
            return {"success": False, "error": str(e)}
    
    # ===================================================================
    # Health & Status
    # ===================================================================
    
    def health_check(self) -> Dict:
        """Check API health"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.json()
        except:
            return {"status": "unhealthy"}
    
    def get_ml_status(self) -> Dict:
        """Get ML model status"""
        return self._get("/ml/status")
    
    # ===================================================================
    # Data Ingestion
    # ===================================================================
    
    def ingest_data(self, data: Dict) -> Dict:
        """
        Ingest single process data point
        
        Args:
            data: Process data
            
        Returns:
            Ingestion result
        """
        return self._post("/data/ingest", data)
    
    def ingest_batch(self, data_list: List[Dict]) -> Dict:
        """
        Ingest batch of process data
        
        Args:
            data_list: List of process data
            
        Returns:
            Ingestion result
        """
        return self._post("/data/ingest/batch", data_list)
    
    def get_latest_data(self, limit: int = 1) -> Dict:
        """
        Get latest process data
        
        Args:
            limit: Number of records
            
        Returns:
            Latest data
        """
        return self._get("/data/latest", params={"limit": limit})
    
    def get_batch_data(self, batch_id: str) -> Dict:
        """
        Get data for specific batch
        
        Args:
            batch_id: Batch identifier
            
        Returns:
            Batch data
        """
        return self._get(f"/data/batch/{batch_id}")
    
    def get_historical_data(
        self,
        hours: int = 24,
        status_filter: Optional[str] = None
    ) -> Dict:
        """
        Get historical data
        
        Args:
            hours: Number of hours to retrieve
            status_filter: Filter by status (GOOD/WARNING/SEVERE)
            
        Returns:
            Historical data
        """
        params = {"hours": hours}
        if status_filter:
            params["status"] = status_filter
        return self._get("/data/historical", params)
    
    def get_data_stats(self) -> Dict:
        """Get data statistics"""
        return self._get("/data/stats")
    
    # ===================================================================
    # ML Predictions
    # ===================================================================
    
    def predict(self, data: Dict) -> Dict:
        """
        Get ML prediction for process data
        
        Args:
            data: Process data
            
        Returns:
            Prediction result
        """
        return self._post("/ml/predict", data)
    
    def predict_batch(self, data_list: List[Dict]) -> Dict:
        """
        Get ML predictions for batch
        
        Args:
            data_list: List of process data
            
        Returns:
            Batch predictions
        """
        return self._post("/ml/predict/batch", data_list)
    
    def explain_prediction(self, data: Dict, top_n: int = 10) -> Dict:
        """
        Get prediction explanation
        
        Args:
            data: Process data
            top_n: Number of top features
            
        Returns:
            Explanation with top features
        """
        return self._post(f"/ml/explain?top_n={top_n}", data)
    
    def get_critical_parameters(
        self,
        data: Dict,
        threshold: float = 0.05
    ) -> Dict:
        """
        Get critical parameters
        
        Args:
            data: Process data
            threshold: Importance threshold
            
        Returns:
            Critical parameters
        """
        return self._post(f"/ml/critical-parameters?threshold={threshold}", data)
    
    def get_recent_predictions(self, limit: int = 100) -> Dict:
        """
        Get recent predictions
        
        Args:
            limit: Number of predictions
            
        Returns:
            Recent predictions
        """
        return self._get("/ml/predictions/recent", params={"limit": limit})
    
    def get_batch_predictions(self, batch_id: str) -> Dict:
        """
        Get predictions for batch
        
        Args:
            batch_id: Batch identifier
            
        Returns:
            Batch predictions
        """
        return self._get(f"/ml/predictions/batch/{batch_id}")
    
    def get_prediction_statistics(self) -> Dict:
        """Get prediction statistics"""
        return self._get("/ml/statistics")
    
    # ===================================================================
    # Utility Methods
    # ===================================================================
    
    def is_connected(self) -> bool:
        """
        Check if API is reachable
        
        Returns:
            True if connected
        """
        health = self.health_check()
        return health.get("status") == "healthy"
    
    def get_api_info(self) -> Dict:
        """
        Get API information
        
        Returns:
            API info
        """
        try:
            response = requests.get(self.base_url, timeout=5)
            return response.json()
        except:
            return {"message": "API not available"}


# Singleton instance
_api_client: Optional[APIClient] = None


def get_api_client(base_url: str = "http://localhost:8000") -> APIClient:
    """
    Get or create API client singleton
    
    Args:
        base_url: Base URL of backend API
        
    Returns:
        API client instance
    """
    global _api_client
    if _api_client is None:
        _api_client = APIClient(base_url=base_url)
    return _api_client


if __name__ == "__main__":
    # Test API client
    print("=== API Client Test ===\n")
    
    client = get_api_client()
    
    # Test connection
    print("Testing connection...")
    if client.is_connected():
        print("✓ API connected")
        
        # Get API info
        info = client.get_api_info()
        print(f"  API: {info.get('message', 'Unknown')}")
        
        # Get ML status
        ml_status = client.get_ml_status()
        print(f"  ML Status: {ml_status.get('status', 'unknown')}")
        
    else:
        print("✗ API not reachable")
        print("  Make sure backend is running: python backend/app/main.py")
    
    print("\n✓ API Client test complete")

# Made with Bob
