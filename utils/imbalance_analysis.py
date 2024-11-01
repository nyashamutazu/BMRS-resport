import pandas as pd
import numpy as np
from datetime import datetime
from utils.helpers import BMRSError

class ImbalanceAnalysis:
    """Class for analysing imbalance costs and rates"""
    
    @staticmethod
    def calculate_daily_imbalance_metrics(prices_df, volumes_df):
        """
        Calculate daily imbalance costs and rates
        """
        try:
            # Ensure DataFrames have matching timestamps
            df = pd.merge(
                prices_df,
                volumes_df,
                on='timestamp',
                how='inner'
            )
            
            # Add date column for grouping
            df['date'] = df['timestamp'].dt.date
            
            # Calculate costs for each settlement period
            df['imbalance_cost'] = np.where(
                df['net_imbalance_volume'] >= 0,
                df['net_imbalance_volume'] * df['system_sell_price'],
                df['net_imbalance_volume'] * df['system_buy_price']
            )
            
            # Calculate daily metrics
            daily_metrics = df.groupby('date').agg({
                'imbalance_cost': 'sum',
                'net_imbalance_volume': 'sum',
                'abs_imbalance_volume': 'sum',
                'system_sell_price': ['mean', 'min', 'max'],
                'system_buy_price': ['mean', 'min', 'max']
            }).round(2)
            
            # Calculate daily unit rate (£/MWh)
            daily_metrics['unit_rate'] = (
                daily_metrics['imbalance_cost'] / 
                daily_metrics['abs_imbalance_volume']
            ).round(2)
            
            return daily_metrics
            
        except Exception as e:
            raise BMRSError(f"Error calculating imbalance metrics: {str(e)}")
    
    @staticmethod
    def generate_daily_report(daily_metrics, date):
        """
        Generate a formatted report message for a specific date
        """
        try:
            # Convert date string to datetime.date
            report_date = datetime.strptime(date, '%Y-%m-%d').date()
            
            # Get metrics for specified date
            metrics = daily_metrics.loc[report_date]
            
            # Format currency values
            cost = f"£{abs(metrics['imbalance_cost']):,.2f}"
            unit_rate = f"£{abs(metrics['unit_rate']):,.2f}"
            
            # Determine if system was long or short overall
            net_position = "LONG" if metrics['net_imbalance_volume'] > 0 else "SHORT"
            
            # Calculate average prices
            avg_sell = metrics[('system_sell_price', 'mean')]
            avg_buy = metrics[('system_buy_price', 'mean')]
            
            # Generate message
            message = (
                f"Daily Imbalance Report for {date}\n"
                f"{'=' * 50}\n\n"
                f"Total Daily Position: {net_position}\n"
                f"Net Imbalance Volume: {metrics['net_imbalance_volume']:,.2f} MWh\n"
                f"Total Imbalance Volume: {metrics['abs_imbalance_volume']:,.2f} MWh\n\n"
                f"Total Imbalance Cost: {cost}\n"
                f"Average Unit Rate: {unit_rate}/MWh\n\n"
                f"Price Statistics:\n"
                f"  System Sell Price (£/MWh):\n"
                f"    Average: £{metrics[('system_sell_price', 'mean')]:,.2f}\n"
                f"    Min: £{metrics[('system_sell_price', 'min')]:,.2f}\n"
                f"    Max: £{metrics[('system_sell_price', 'max')]:,.2f}\n"
                f"  System Buy Price (£/MWh):\n"
                f"    Average: £{metrics[('system_buy_price', 'mean')]:,.2f}\n"
                f"    Min: £{metrics[('system_buy_price', 'min')]:,.2f}\n"
                f"    Max: £{metrics[('system_buy_price', 'max')]:,.2f}\n\n"
                f"Average Price Spread: £{(avg_buy - avg_sell):,.2f}/MWh"
            )
            
            return message
            
        except Exception as e:
            raise BMRSError(f"Error generating report: {str(e)}")
    
    @staticmethod
    def generate_multi_day_summary(daily_metrics):
        """
        Generate a summary for multiple days
        """
        try:
            # Calculate period statistics
            total_cost = daily_metrics['imbalance_cost'].sum()
            total_volume = daily_metrics['abs_imbalance_volume'].sum()
            avg_unit_rate = total_cost / total_volume
            
            # Get date range
            start_date = daily_metrics.index.min()
            end_date = daily_metrics.index.max()
            num_days = (end_date - start_date).days + 1
            
            message = (
                f"Imbalance Summary Report\n"
                f"{'=' * 50}\n"
                f"Period: {start_date} to {end_date} ({num_days} days)\n\n"
                f"Total Statistics:\n"
                f"  Total Imbalance Cost: £{abs(total_cost):,.2f}\n"
                f"  Total Imbalance Volume: {total_volume:,.2f} MWh\n"
                f"  Average Daily Cost: £{abs(total_cost/num_days):,.2f}\n"
                f"  Average Unit Rate: £{abs(avg_unit_rate):,.2f}/MWh\n\n"
                f"Daily Averages:\n"
                f"  System Sell Price: £{daily_metrics[('system_sell_price', 'mean')].mean():,.2f}/MWh\n"
                f"  System Buy Price: £{daily_metrics[('system_buy_price', 'mean')].mean():,.2f}/MWh\n"
                f"  Imbalance Volume: {daily_metrics['abs_imbalance_volume'].mean():,.2f} MWh"
            )
            
            return message
            
        except Exception as e:
            raise BMRSError(f"Error generating summary: {str(e)}")