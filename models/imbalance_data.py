from dataclasses import dataclass
from datetime import datetime

@dataclass
class ImbalanceData:
    """Data class for imbalance data"""
    timestamp: datetime
    settlement_period: int
    system_buy_price: float
    system_sell_price: float
    net_imbalance_volume: float
    settlement_date: str
    
    @classmethod
    def from_api_response(cls, data: dict) -> 'ImbalanceData':
        """Create ImbalanceData from API response"""
        return cls(
            timestamp=datetime.fromisoformat(data['startTime'].rstrip('Z')),
            settlement_period=data['settlementPeriod'],
            system_buy_price=float(data['systemBuyPrice']),
            system_sell_price=float(data['systemSellPrice']),
            net_imbalance_volume=float(data['netImbalanceVolume']),
            settlement_date=data['settlementDate']
        )
