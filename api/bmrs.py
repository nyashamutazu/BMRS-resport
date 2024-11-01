import requests
import pandas as pd
from datetime import datetime, timedelta
import logging
from utils.helpers import BMRSError

class BMRSApi:
    """Class for calling BMRS System Prices API endpoint"""
    
    def __init__(self):
        """Initialise the BMRS API"""
        
        self.base_url = "https://data.elexon.co.uk/bmrs/api/v1"
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def get_imbalance_data(self, settlement_date):
        """
        Fetch imbalance prices for a given settlement date
        """
        
        try:
            # Validate date format
            datetime.strptime(settlement_date, '%Y-%m-%d')
            
            # Construct the endpoint URL
            endpoint = f"{self.base_url}/balancing/settlement/system-prices/{settlement_date}"
            params = {'format': 'json'}
            
            # Make the API request
            self.logger.info(f"Fetching system prices data for {settlement_date}")
            
            response = requests.get(endpoint, params=params)
            
            # Log request details
            self.logger.info(f"Request URL: {response.url}")
            self.logger.info(f"Response status code: {response.status_code}")
            
            # Check if request was successful
            response.raise_for_status()
            
            # Parse JSON response
            response_data = response.json()
            
            # Check if data exists in response
            if not response_data or 'data' not in response_data:
                raise BMRSError(f"No data returned for {settlement_date}")
            
            # Define expected columns and their types
            column_types = {
                'settlementDate': 'str',
                'settlementPeriod': 'int',
                'startTime': 'str',
                'systemSellPrice': 'float',
                'systemBuyPrice': 'float',
                'netImbalanceVolume': 'float',
                'totalAcceptedOfferVolume': 'float',
                'totalAcceptedBidVolume': 'float'
            }
            
            # Convert to DataFrame with specified dtypes
            df = pd.DataFrame(response_data['data'])
            
            # Convert columns to specified types
            for col, dtype in column_types.items():
                if col in df.columns:
                    df[col] = df[col].astype(dtype)
            
            # Convert startTime to timestamp
            df['timestamp'] = pd.to_datetime(df['startTime'])
            
            # Sort by settlement period
            df = df.sort_values(['settlementDate', 'settlementPeriod'])
            
            self.logger.info(f"Successfully retrieved {len(df)} periods for {settlement_date}")
            
            return df
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {str(e)}")
            raise BMRSError(f"Failed to fetch data: {str(e)}")
        except ValueError as e:
            self.logger.error(f"Invalid date format: {str(e)}")
            raise BMRSError(f"Invalid date format. Required: YYYY-MM-DD")
        except Exception as e:
            self.logger.error(f"Error processing data: {str(e)}")
            raise BMRSError(f"Error processing data: {str(e)}")

    def get_historic_imbalance_data(self, start_date, end_date):
        """
        Fetch historic imbalance data for a date range
        """
        
        try:
            # Validate dates
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            
            if end < start:
                raise BMRSError("End date must be after start date")
            
            # Fetch data for each day
            all_data = []
            current_date = start
            
            while current_date <= end:
                date_str = current_date.strftime('%Y-%m-%d')
                try:
                    df = self.get_imbalance_data(date_str)
                    if not df.empty:  # Only append non-empty DataFrames
                        all_data.append(df)
                    self.logger.info(f"Successfully retrieved data for {date_str}")
                except BMRSError as e:
                    self.logger.warning(f"Failed to fetch data for {date_str}: {str(e)}")
                current_date += timedelta(days=1)
            
            if not all_data:
                raise BMRSError("No data retrieved for the specified date range")
                
            # Ensure all DataFrames have the same columns before concatenation
            common_columns = set.intersection(*[set(df.columns) for df in all_data])
            all_data = [df[list(common_columns)] for df in all_data]
            
            # Concatenate all data
            combined_df = pd.concat(all_data, ignore_index=True)
            
            # Sort by timestamp
            combined_df = combined_df.sort_values('timestamp')
            
            self.logger.info(f"Successfully retrieved data for {len(all_data)} days")
            
            return combined_df
            
        except Exception as e:
            self.logger.error(f"Error fetching historic data: {str(e)}")
            raise BMRSError(f"Error fetching historic data: {str(e)}")