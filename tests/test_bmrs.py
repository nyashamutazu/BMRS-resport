import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from api.bmrs import BMRSApi
from utils.helpers import BMRSError

@pytest.fixture
def mock_response():
    """Create a mock API response"""
    return {
        'data': [
            {
                'settlementDate': '2024-03-01',
                'settlementPeriod': 1,
                'systemSellPrice': 100.5,
                'systemBuyPrice': 110.5,
                'netImbalanceVolume': -500
            }
        ]
    }

@pytest.fixture
def api():
    """Create an API api instance with a dummy key"""
    return BMRSApi()

def test_init():
    """Test initialisation"""
    with pytest.raises(BMRSError):
        BMRSApi()

@patch('requests.get')
def test_get_imbalance_data_success(mock_get, api, mock_response):
    """Test successful data retrieval"""
    # Setup mock
    mock_get.return_value.json.return_value = mock_response
    mock_get.return_value.raise_for_status = MagicMock()
    
    # Call method
    df = api.get_imbalance_data('2024-03-01')
    
    # Verify results
    assert len(df) == 1
    assert df.iloc[0]['systemSellPrice'] == 100.5
    assert df.iloc[0]['systemBuyPrice'] == 110.5
    assert df.iloc[0]['netImbalanceVolume'] == -500

@patch('requests.get')
def test_get_imbalance_data_api_error(mock_get, api):
    """Test API error handling"""
    # Setup mock to raise an error
    mock_get.side_effect = Exception("API Error")
    
    # Verify error handling
    with pytest.raises(BMRSError):
        api.get_imbalance_data('2024-03-01')

def test_invalid_settlement_period(api):
    """Test invalid settlement period validation"""
    with pytest.raises(BMRSError):
        api.get_imbalance_data('2024-03-01', settlement_period=49)

def test_invalid_date_format(api):
    """Test invalid date format validation"""
    with pytest.raises(BMRSError):
        api.get_imbalance_data('2024/03/01')

@patch('requests.get')
def test_get_historic_imbalance_data(mock_get, api, mock_response):
    """Test historic data retrieval"""
    # Setup mock
    mock_get.return_value.json.return_value = mock_response
    mock_get.return_value.raise_for_status = MagicMock()
    
    # Call method
    df = api.get_historic_imbalance_data('2024-03-01', '2024-03-02')
    
    # Verify results
    assert len(df) == 2  # Two days of data
    assert mock_get.call_count == 2  # Two API calls made