import logging
import sys
from analysis.bmrs import BMRSAnalysis
from utils.helpers import BMRSError, setup_logging, display_results
from ui.visual import VisualisationService

def main():
    """Main application"""
    try:
        # Setup logging
        setup_logging()
        logger = logging.getLogger(__name__)
        
        # Initialise analysis
        analysis = BMRSAnalysis()
        ui_service = VisualisationService()
        
        # Define analysis period
        start_date = '2024-03-01'
        end_date = '2024-03-07'
        
        logger.info(f"Starting analysis for period {start_date} to {end_date}")
        
        # Run analysis
        results = analysis.run_analysis(start_date, end_date)
        
        # Get the processed DataFrames
        prices_df, volumes_df = analysis.get_dataframes()
        
        # Display results
        display_results(results)
        
        ui_service.save_analysis_dashboard(
            results,
            prices_df,
            volumes_df,
            filename='bmrs_dashboard.html'
        )
        
        print("\nAnalysis complete. Dashboard saved to 'bmrs_dashboard.html'")
        
        logger.info("Analysis completed successfully")
        
    except BMRSError as e:
        logger.error(f"Analysis failed: {str(e)}")
        print(f"\nError: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"\nUnexpected error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()