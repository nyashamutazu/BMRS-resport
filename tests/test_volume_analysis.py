import pytest
import pandas as pd
import numpy as np
from utils.helpers import BMRSError
from utils.volume_analysis import VolumeAnalysis

@pytest.fixture
def sample_volume_data():
    """Create sample volume data for testing"""
    # Create timestamps for 2 days
    dates = pd.date_range(
        start='2024-03-01',
        periods=96,  # Two days of half-hourly periods
        freq='30min'
    )
    
    # Create volumes DataFrame with a known pattern
    volumes_df = pd.DataFrame({
        'timestamp': dates,
        'net_imbalance_volume': np.concatenate([
            np.random.uniform(-500, -1000, 48),  # Day 1: mostly short
            np.random.uniform(500, 1000, 48)     # Day 2: mostly long
        ]),
        'volume_quality': 'Good'
    })
    
    # Add absolute volumes
    volumes_df['abs_imbalance_volume'] = abs(volumes_df['net_imbalance_volume'])
    
    # Create a known peak hour
    peak_hour = 14  # 2 PM
    volumes_df.loc[volumes_df['timestamp'].dt.hour == peak_hour, 'abs_imbalance_volume'] *= 2
    
    return volumes_df

def test_analyse_hourly_volumes(sample_volume_data):
    """Test hourly volume analysis"""
    hourly_stats, report = VolumeAnalysis.analyse_hourly_volumes(sample_volume_data)
    
    # Check basic structure
    assert isinstance(hourly_stats, pd.DataFrame)
    assert isinstance(report, str)
    assert len(hourly_stats) == 24  # 24 hours
    
    # Check report content
    assert "Top 3 Hours by Total Volume" in report
    assert "Most Frequent Peak Hours" in report
    assert "Highest Single Hour" in report

def test_daily_peak_report(sample_volume_data):
    """Test daily peak hours report"""
    report = VolumeAnalysis.generate_daily_peak_report(
        sample_volume_data,
        '2024-03-01'
    )
    
    # Check report content
    assert "Daily Peak Hours Report for 2024-03-01" in report
    assert "Top 3 Hours by Volume" in report
    assert "Net Position" in report

def test_error_handling():
    """Test error handling with invalid data"""
    with pytest.raises(BMRSError):
        VolumeAnalysis.analyse_hourly_volumes(pd.DataFrame())  # Empty DataFrame

def test_known_peak_hour(sample_volume_data):
    """Test identification of known peak hour"""
    hourly_stats, report = VolumeAnalysis.analyse_hourly_volumes(sample_volume_data)
    
    # The peak hour (14:00) should be among the top hours
    assert "14:00-15:00" in report