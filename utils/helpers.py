from datetime import datetime
import logging
import re
import sys

class BMRSError(Exception):
    """Custom exception class for BMRS-related errors"""
    pass

def validate_date_format(date_string):
    """
    Validate that a date string matches YYYY-MM-DD format
    """
    # Check basic format
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_string):
        raise BMRSError(f"Invalid date format: {date_string}. Expected format: YYYY-MM-DD")
    
    try:
        # Check if it's a valid date
        datetime.strptime(date_string, '%Y-%m-%d')
    except ValueError as e:
        raise BMRSError(f"Invalid date: {date_string}. {str(e)}")

def validate_settlement_period(period):
    """
    Validate that a settlement period is between 1 and 48
    """
    try:
        period_int = int(period)
        if not 1 <= period_int <= 48:
            raise BMRSError(f"Settlement period must be between 1 and 48, got: {period}")
    except ValueError:
        raise BMRSError(f"Settlement period must be an integer, got: {period}")
    
    
def setup_logging():
    """Configure logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bmrs_analysis.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def display_results(results):
    """Display analysis results"""
    print("\nPeak Hours Analysis:")
    print("=" * 50)
    print(results.peak_hours_report)
    
    print("\nDaily Reports:")
    print("=" * 50)
    for date, report in results.daily_reports.items():
        print(f"\nReport for {date}:")
        print(report)
    
    print("\nData Quality Metrics:")
    print("=" * 50)
    for category, metrics in results.data_quality.items():
        print(f"\n{category.title()}:")
        for metric, value in metrics.items():
            print(f"  {metric}: {value:.2f}%")