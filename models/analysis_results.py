
from dataclasses import dataclass
import pandas as pd
from typing import Dict

@dataclass
class AnalysisResult:
    """Data class for analysis results"""
    hourly_stats: pd.DataFrame
    peak_hours_report: str
    daily_reports: Dict[str, str]
    data_quality: Dict[str, Dict[str, float]]


