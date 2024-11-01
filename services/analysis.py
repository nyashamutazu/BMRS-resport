from typing import Tuple
import pandas as pd

class AnalysisService:
    """Service class for data analysis"""
    
    @staticmethod
    def analyse_volumes(volumes_df: pd.DataFrame) -> Tuple[pd.DataFrame, str]:
        """Analyse volume patterns"""
        hourly_stats = volumes_df.groupby(volumes_df['timestamp'].dt.hour).agg({
            'abs_imbalance_volume': ['mean', 'sum', 'std']
        })
        
        report = AnalysisService._generate_volume_report(hourly_stats)
        return hourly_stats, report
    
    @staticmethod
    def _generate_volume_report(stats: pd.DataFrame) -> str:
        """Generate formatted volume report"""
        peak_hour = stats['abs_imbalance_volume']['sum'].idxmax()
        peak_volume = stats['abs_imbalance_volume']['sum'].max()
        
        return (
            f"Volume Analysis Report\n"
            f"{'=' * 50}\n"
            f"Peak Hour: {peak_hour:02d}:00\n"
            f"Peak Volume: {peak_volume:,.2f} MWh\n"
        )