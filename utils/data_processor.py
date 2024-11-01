import pandas as pd
import numpy as np
from utils.helpers import BMRSError

class BMRSDataProcessor:
    """Class for processing and cleaning BMRS data"""
    
    @staticmethod
    def clean_and_process_data(df):
        """
        Clean and process raw BMRS data
        """
        
        try:
            # Make a copy to avoid modifying original data
            df = df.copy()
            
            # Convert columns to numeric, replacing any non-numeric values with NaN
            numeric_columns = ['systemSellPrice', 'systemBuyPrice', 'netImbalanceVolume']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Sort by timestamp
            df = df.sort_values('timestamp')
            
            # Check for missing periods
            expected_periods = pd.date_range(
                start=df['timestamp'].min(),
                end=df['timestamp'].max(),
                freq='30min'
            )
            
            # Create a template DataFrame with all expected periods
            template_df = pd.DataFrame({'timestamp': expected_periods})
            
            # Merge with actual data
            df = pd.merge(template_df, df, on='timestamp', how='left')
            
            # Store interpolation mask before interpolating
            is_interpolated_sell = df['systemSellPrice'].isna()
            is_interpolated_buy = df['systemBuyPrice'].isna()
            
            # Convert to float type before interpolation
            df = df.astype({col: 'float64' for col in numeric_columns if col in df.columns})
            
            # Interpolate missing values (limited to 2 consecutive periods)
            df = df.interpolate(method='linear', limit=2)
            
            # Create prices DataFrame
            prices_df = pd.DataFrame({
                'timestamp': df['timestamp'],
                'system_sell_price': df['systemSellPrice'],
                'system_buy_price': df['systemBuyPrice'],
                'price_spread': df['systemBuyPrice'] - df['systemSellPrice'],
                'is_interpolated_sell': is_interpolated_sell,
                'is_interpolated_buy': is_interpolated_buy
            })
            
            # Create volumes DataFrame
            volumes_df = pd.DataFrame({
                'timestamp': df['timestamp'],
                'net_imbalance_volume': df['netImbalanceVolume'],
                'abs_imbalance_volume': df['netImbalanceVolume'].abs()
            })
            
            # Add quality flags
            prices_df['price_quality'] = BMRSDataProcessor._get_price_quality_flag(prices_df)
            volumes_df['volume_quality'] = BMRSDataProcessor._get_volume_quality_flag(volumes_df)
            
            return prices_df, volumes_df
            
        except Exception as e:
            raise BMRSError(f"Error processing data: {str(e)}")
    
    @staticmethod
    def _get_price_quality_flag(df):
        """
        Generate quality flags for price data
        """
        
        conditions = [
            df['system_sell_price'].isna() | df['system_buy_price'].isna(),
            df['is_interpolated_sell'] | df['is_interpolated_buy'],
            df['price_spread'] < 0  # Anomaly: sell price higher than buy price
        ]
        choices = ['Missing', 'Interpolated', 'Anomaly']
        return pd.Series(np.select(conditions, choices, default='Good'))
    
    @staticmethod
    def _get_volume_quality_flag(df):
        """
        Generate quality flags for volume data
        """
        
        conditions = [
            df['net_imbalance_volume'].isna(),
            df['net_imbalance_volume'].isna() & df['net_imbalance_volume'].notna()  # Was interpolated
        ]
        choices = ['Missing', 'Interpolated']
        return pd.Series(np.select(conditions, choices, default='Good'))
    
    @staticmethod
    def get_data_quality_summary(prices_df, volumes_df):
        """
        Generate a summary of data quality
        """
        
        summary = {
            'prices': {
                'total_periods': len(prices_df),
                'missing_periods': (prices_df['price_quality'] == 'Missing').sum(),
                'interpolated_periods': (prices_df['price_quality'] == 'Interpolated').sum(),
                'anomalies': (prices_df['price_quality'] == 'Anomaly').sum()
            },
            'volumes': {
                'total_periods': len(volumes_df),
                'missing_periods': (volumes_df['volume_quality'] == 'Missing').sum(),
                'interpolated_periods': (volumes_df['volume_quality'] == 'Interpolated').sum()
            }
        }
        
        # Add percentages
        for metric in ['prices', 'volumes']:
            total = summary[metric]['total_periods']
            for key in list(summary[metric].keys())[1:]:
                summary[metric][f'{key}_pct'] = (summary[metric][key] / total * 100)
                
        return summary