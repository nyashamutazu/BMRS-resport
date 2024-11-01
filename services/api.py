from typing import List
import requests
import logging
from models.imbalance_data import ImbalanceData
from utils.helpers import BMRSError

class APIService:
    """Service class for API interactions"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)

    def get_imbalance_data(self, settlement_date: str) -> List[ImbalanceData]:
        """Fetch imbalance data for a single date"""
        try:
            endpoint = f"{self.base_url}/balancing/settlement/system-prices/{settlement_date}"
            params = {'format': 'json'}
            
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if not data or 'data' not in data:
                raise BMRSError(f"No data returned for {settlement_date}")
                
            return [ImbalanceData.from_api_response(item) for item in data['data']]
            
        except Exception as e:
            self.logger.error(f"API error: {str(e)}")
            raise BMRSError(f"Failed to fetch data: {str(e)}")