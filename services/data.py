import pandas as pd
from typing import Tuple, List
from models.imbalance_data import ImbalanceData

class DataService:
    """Service class for data processing"""
    
    @staticmethod
    def convert_to_dataframe(data: List[ImbalanceData]) -> pd.DataFrame:
        """Convert list of ImbalanceData to DataFrame"""
        return pd.DataFrame([vars(item) for item in data])
    
    @staticmethod
    def process_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Process raw data into prices and volumes DataFrames"""
        # Prices DataFrame
        prices_df = pd.DataFrame({
            'timestamp': df['timestamp'],
            'system_sell_price': df['system_sell_price'],
            'system_buy_price': df['system_buy_price'],
            'price_spread': df['system_buy_price'] - df['system_sell_price']
        })
        
        # Volumes DataFrame
        volumes_df = pd.DataFrame({
            'timestamp': df['timestamp'],
            'net_imbalance_volume': df['net_imbalance_volume'],
            'abs_imbalance_volume': abs(df['net_imbalance_volume'])
        })
        
        return prices_df, volumes_df
