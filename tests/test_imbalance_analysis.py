import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils.imbalance_analysis import ImbalanceAnalysis
from utils.helpers import BMRSError

@pytest.fixture
def sample_processed_data():
    """Create sample processed data for testing"""
    # Create timestamps for 2 days
    dates = pd.date_range(
        start='2024-03-01',
        periods=96,  # Two days of half-hourly periods
        freq='30min'
    )
    
    # Create prices DataFrame
    prices_df = pd.DataFrame({
        'timestamp': dates,
        'system_sell_price': np.random.uniform(80, 90, 96),
        'system_buy_price': np.random.uniform(90, 100, 96),
        'price_spread': np.random.uniform(5, 15, 96),
        'price_quality': 'Good'
    })
    
    # Create volumes DataFrame
    volumes_df = pd.DataFrame({
        'timestamp': dates,
        'net_imbalance_volume': np.random.uniform(-1000, 1000, 96),
        'abs_imbalance_volume': np.random.uniform(0, 1000, 96),
        'volume_quality': 'Good'
    })
    
    return prices_df, volumes_df

def test_calculate_daily_metrics(sample_processed_data):
    """Test calculation of daily metrics"""
    prices_df, volumes_df = sample_processed_data
    daily_metrics = ImbalanceAnalysis.calculate_daily_imbalance_metrics(prices_df, volumes_df)
    
    # Check basic structure
    assert len(daily_metrics) == 2  # Two days of data
    assert 'imbalance_cost' in daily_metrics.columns
    assert 'unit_rate' in daily_metrics.columns

def test_generate_daily_report(sample_processed_data):
    """Test daily report generation"""
    prices_df, volumes_df = sample_processed_data
    daily_metrics = ImbalanceAnalysis.calculate_daily_imbalance_metrics(prices_df, volumes_df)
    
    report = ImbalanceAnalysis.generate_daily_report(daily_metrics, '2024-03-01')
    
    # Check report content
    assert 'Daily Imbalance Report for 2024-03-01' in report
    assert 'Total Imbalance Cost' in report
    assert 'Average Unit Rate' in report

def test_generate_multi_day_summary(sample_processed_data):
    """Test multi-day summary generation"""
    prices_df, volumes_df = sample_processed_data
    daily_metrics = ImbalanceAnalysis.calculate_daily_imbalance_metrics(prices_df, volumes_df)
    
    summary = ImbalanceAnalysis.generate_multi_day_summary(daily_metrics)
    
    # Check summary content
    assert 'Imbalance Summary Report' in summary
    assert 'Total Statistics' in summary
    assert 'Daily Averages' in summary

def test_error_handling():
    """Test error handling with invalid data"""
    with pytest.raises(BMRSError):
        ImbalanceAnalysis.calculate_daily_imbalance_metrics(
            pd.DataFrame(),  # Empty DataFrame
            pd.DataFrame()
        )