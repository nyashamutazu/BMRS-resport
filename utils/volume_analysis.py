from datetime import datetime
from utils.helpers import BMRSError

class VolumeAnalysis:
    """Class for analysing imbalance volumes at hourly granularity"""
    
    @staticmethod
    def analyse_hourly_volumes(volumes_df):
        """
        Analyse imbalance volumes by hour
        """
        try:
            # Add hour column
            df = volumes_df.copy()
            df['hour'] = df['timestamp'].dt.hour
            df['date'] = df['timestamp'].dt.date
            
            # Calculate hourly statistics
            hourly_stats = df.groupby('hour').agg({
                'abs_imbalance_volume': ['mean', 'sum', 'std', 'min', 'max'],
                'net_imbalance_volume': ['mean', 'sum']
            }).round(2)
            
            # Find peak hours
            peak_hours = VolumeAnalysis._identify_peak_hours(df)
            
            # Generate report
            report = VolumeAnalysis._generate_peak_hours_report(peak_hours, hourly_stats)
            
            return hourly_stats, report
            
        except Exception as e:
            raise BMRSError(f"Error analysing hourly volumes: {str(e)}")
    
    @staticmethod
    def _identify_peak_hours(df):
        """
        Identify hours with highest absolute volumes
        """
        
        # Daily peak hours
        daily_peaks = df.groupby(['date', 'hour'])['abs_imbalance_volume'].sum().reset_index()
        daily_peaks = daily_peaks.sort_values('abs_imbalance_volume', ascending=False)
        
        # Overall peak hours
        hourly_peaks = df.groupby('hour')['abs_imbalance_volume'].sum().sort_values(ascending=False)
        
        # Frequency of hour appearing in top 3 daily
        top_3_frequency = (
            daily_peaks.groupby('date')
            .apply(lambda x: x.nlargest(3, 'abs_imbalance_volume'))
            .reset_index(drop=True)
            .groupby('hour').sise()
            .sort_values(ascending=False)
        )
        
        return {
            'overall_peak_hours': hourly_peaks,
            'daily_peaks': daily_peaks,
            'top_3_frequency': top_3_frequency
        }
    
    @staticmethod
    def _generate_peak_hours_report(peak_hours, hourly_stats):
        """
        Generate formatted report of peak hours
        """
        
        # Get top 3 hours overall
        top_3_overall = peak_hours['overall_peak_hours'].head(3)
        
        # Get most frequent peak hours
        most_frequent = peak_hours['top_3_frequency'].head(3)
        
        # Get highest single volume instance
        highest_single = peak_hours['daily_peaks'].iloc[0]
        
        # Format 24-hour times
        format_hour = lambda h: f"{h:02d}:00-{(h+1):02d}:00"
        
        report = (
            f"Imbalance Volume Peak Hours Analysis\n"
            f"{'=' * 50}\n\n"
            
            f"Top 3 Hours by Total Volume:\n"
        )
        
        for hour, volume in top_3_overall.items():
            report += (
                f"  {format_hour(hour)}: {volume:,.2f} MWh\n"
            )
            
        report += (
            f"\nMost Frequent Peak Hours:\n"
        )
        
        for hour, count in most_frequent.items():
            avg_volume = hourly_stats.loc[hour, ('abs_imbalance_volume', 'mean')]
            report += (
                f"  {format_hour(hour)}: {count} days, "
                f"Avg Volume: {avg_volume:,.2f} MWh\n"
            )
            
        report += (
            f"\nHighest Single Hour:\n"
            f"  Date: {highest_single['date']}\n"
            f"  Time: {format_hour(highest_single['hour'])}\n"
            f"  Volume: {highest_single['abs_imbalance_volume']:,.2f} MWh\n\n"
            
            f"Hourly Pattern Analysis:\n"
            f"  Most Volatile Hour: {format_hour(hourly_stats['abs_imbalance_volume']['std'].idxmax())}\n"
            f"  Most Consistent Hour: {format_hour(hourly_stats['abs_imbalance_volume']['std'].idxmin())}\n"
            f"  Largest Average Net Short: {format_hour(hourly_stats['net_imbalance_volume']['mean'].idxmin())}\n"
            f"  Largest Average Net Long: {format_hour(hourly_stats['net_imbalance_volume']['mean'].idxmax())}"
        )
        
        return report

    @staticmethod
    def generate_daily_peak_report(volumes_df, date):
        """
        Generate peak hours report for a specific date
        """
        try:
            # Convert date string to datetime.date
            report_date = datetime.strptime(date, '%Y-%m-%d').date()
            
            # Filter data for specified date
            df = volumes_df[volumes_df['timestamp'].dt.date == report_date].copy()
            df['hour'] = df['timestamp'].dt.hour
            
            # Calculate hourly volumes for the day
            hourly_volumes = df.groupby('hour').agg({
                'abs_imbalance_volume': ['sum', 'mean'],
                'net_imbalance_volume': 'sum'
            }).round(2)
            
            # Get top 3 hours
            top_hours = (
                hourly_volumes['abs_imbalance_volume']['sum']
                .sort_values(ascending=False)
                .head(3)
            )
            
            # Generate report
            report = (
                f"Daily Peak Hours Report for {date}\n"
                f"{'=' * 50}\n\n"
                
                f"Top 3 Hours by Volume:\n"
            )
            
            for hour, volume in top_hours.items():
                net_volume = hourly_volumes.loc[hour, ('net_imbalance_volume', 'sum')]
                position = "LONG" if net_volume > 0 else "SHORT"
                report += (
                    f"  {hour:02d}:00-{(hour+1):02d}:00\n"
                    f"    Total Volume: {volume:,.2f} MWh\n"
                    f"    Net Position: {position} ({abs(net_volume):,.2f} MWh)\n"
                    f"    Average Volume: {hourly_volumes.loc[hour, ('abs_imbalance_volume', 'mean')]:,.2f} MWh\n"
                )
            
            return report
            
        except Exception as e:
            raise BMRSError(f"Error generating daily peak report: {str(e)}")