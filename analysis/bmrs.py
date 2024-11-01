from datetime import datetime, timedelta
import logging
from typing import Dict, Tuple
import pandas as pd
from models.analysis_results import AnalysisResult
from services.analysis import AnalysisService
from services.api import APIService
from services.data import DataService
from utils.helpers import BMRSError

class BMRSAnalysis:
    """Main class for BMRS analysis"""
    
    def __init__(self):
        self.api_service = APIService("https://data.elexon.co.uk/bmrs/api/v1")
        self.data_service = DataService()
        self.analysis_service = AnalysisService()
        self.logger = logging.getLogger(__name__)
        self._raw_data = None
        self._prices_df = None
        self._volumes_df = None

    def run_analysis(self, start_date: str, end_date: str) -> AnalysisResult:
        """Run complete analysis pipeline"""
        try:
            # Validate dates
            self._validate_dates(start_date, end_date)
            
            # Fetch data
            raw_data = []
            current_date = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            
            while current_date <= end:
                date_str = current_date.strftime('%Y-%m-%d')
                data = self.api_service.get_imbalance_data(date_str)
                raw_data.extend(data)
                current_date += timedelta(days=1)
            
            # Store raw data
            self._raw_data = self.data_service.convert_to_dataframe(raw_data)
            
            # Process data
            self._prices_df, self._volumes_df = self.data_service.process_data(self._raw_data)
            
            # Analyse data
            hourly_stats, peak_hours_report = self.analysis_service.analyse_volumes(self._volumes_df)
            
            # Generate daily reports
            daily_reports = self._generate_daily_reports(self._volumes_df, start_date, end_date)
            
            # Calculate data quality metrics
            quality_metrics = self._calculate_quality_metrics(self._prices_df, self._volumes_df)
            
            return AnalysisResult(
                hourly_stats=hourly_stats,
                peak_hours_report=peak_hours_report,
                daily_reports=daily_reports,
                data_quality=quality_metrics
            )
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {str(e)}")
            raise BMRSError(f"Analysis failed: {str(e)}")

    def get_dataframes(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Get the processed price and volume DataFrames"""
        if self._prices_df is None or self._volumes_df is None:
            raise BMRSError("Analysis must be run before accessing DataFrames")
        return self._prices_df, self._volumes_df
    
    def _validate_dates(self, start_date: str, end_date: str):
        """Validate input dates"""
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            
            if end < start:
                raise ValueError("End date must be after start date")
                
            if (end - start).days > 31:
                raise ValueError("Date range cannot exceed 31 days")
                
        except ValueError as e:
            raise BMRSError(f"Invalid dates: {str(e)}")
    
    def _generate_daily_reports(self, volumes_df: pd.DataFrame, 
                              start_date: str, end_date: str) -> Dict[str, str]:
        """Generate reports for each day"""
        reports = {}
        current_date = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        while current_date <= end:
            date_str = current_date.strftime('%Y-%m-%d')
            daily_data = volumes_df[volumes_df['timestamp'].dt.date == current_date.date()]
            
            if not daily_data.empty:
                _, report = self.analysis_service.analyse_volumes(daily_data)
                reports[date_str] = report
                
            current_date += timedelta(days=1)
            
        return reports
    
    def _calculate_quality_metrics(self, prices_df: pd.DataFrame, 
                                 volumes_df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """Calculate data quality metrics"""
        return {
            'prices': {
                'missing_rate': prices_df.isnull().mean().mean() * 100,
                'anomaly_rate': (prices_df['price_spread'] < 0).mean() * 100
            },
            'volumes': {
                'missing_rate': volumes_df.isnull().mean().mean() * 100,
                'sero_volume_rate': (volumes_df['abs_imbalance_volume'] == 0).mean() * 100
            }
        }