import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from models.analysis_results import AnalysisResult

class VisualisationService:
    """Service for creating interactive visualisations of BMRS data"""
    
    def create_analysis_dashboard(self, analysis_result: AnalysisResult,
                                prices_df: pd.DataFrame, volumes_df: pd.DataFrame) -> go.Figure:
        """Create a comprehensive dashboard with analysis results and visualisations"""
        
        # Create figure with secondary axis
        fig = make_subplots(
            rows=4, cols=2,
            subplot_titles=(
                'System Prices Over Time',
                'Imbalance Volumes',
                'Hourly Volume Statistics',
                'Volume Distribution',
                'Price-Volume Correlation',
                'Daily Statistics',
                'Data Quality Metrics',
                'Peak Hours Analysis'
            ),
            specs=[
                [{"secondary_y": True}, {"secondary_y": True}],
                [{"type": "box"}, {"type": "histogram"}],
                [{"type": "scatter"}, {"type": "bar"}],
                [{"type": "table"}, {"type": "table"}]
            ],
            vertical_spacing=0.1
        )

        # 1. System Prices Time Series
        fig.add_trace(
            go.Scatter(
                x=prices_df['timestamp'],
                y=prices_df['system_buy_price'],
                name="Buy Price",
                line=dict(color='#1f77b4')
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=prices_df['timestamp'],
                y=prices_df['system_sell_price'],
                name="Sell Price",
                line=dict(color='#ff7f0e')
            ),
            row=1, col=1
        )

        # 2. Imbalance Volumes
        fig.add_trace(
            go.Scatter(
                x=volumes_df['timestamp'],
                y=volumes_df['net_imbalance_volume'],
                name="Net Imbalance Volume",
                line=dict(color='#2ca02c')
            ),
            row=1, col=2
        )

        # 3. Hourly Volume Statistics from analysis_result
        hourly_stats_df = analysis_result.hourly_stats.reset_index()
        fig.add_trace(
            go.Box(
                x=hourly_stats_df.index,
                y=hourly_stats_df[('abs_imbalance_volume', 'sum')],
                name="Hourly Volume Distribution",
                boxmean=True
            ),
            row=2, col=1
        )

        # 4. Volume Distribution
        fig.add_trace(
            go.Histogram(
                x=volumes_df['net_imbalance_volume'],
                name="Volume Distribution",
                nbinsx=30,
                histnorm='probability'
            ),
            row=2, col=2
        )

        # 5. Price-Volume Correlation
        fig.add_trace(
            go.Scatter(
                x=volumes_df['net_imbalance_volume'],
                y=prices_df['system_buy_price'],
                mode='markers',
                name='Price vs Volume',
                marker=dict(
                    size=8,
                    color=prices_df['system_buy_price'],
                    colorscale='Viridis',
                    showscale=True
                )
            ),
            row=3, col=1
        )

        # 6. Daily Statistics
        daily_volumes = volumes_df.groupby(
            volumes_df['timestamp'].dt.date
        )['net_imbalance_volume'].agg(['mean', 'std']).reset_index()
        
        fig.add_trace(
            go.Bar(
                x=daily_volumes['timestamp'],
                y=daily_volumes['mean'],
                name='Daily Mean Volume',
                error_y=dict(
                    type='data',
                    array=daily_volumes['std'],
                    visible=True
                )
            ),
            row=3, col=2
        )

        # 7. Data Quality Table
        quality_data = pd.DataFrame([
            ['Prices', f"{v:.2f}%" if isinstance(v, float) else v] 
            for k, v in analysis_result.data_quality['prices'].items()
        ])
        
        fig.add_trace(
            go.Table(
                header=dict(
                    values=['Metric', 'Value'],
                    fill_color='paleturquoise',
                    align='left'
                ),
                cells=dict(
                    values=quality_data.T.values,
                    fill_color='lavender',
                    align='left'
                )
            ),
            row=4, col=1
        )

        # 8. Peak Hours Summary
        peak_hours_text = analysis_result.peak_hours_report.split('\n')
        peak_hours_data = pd.DataFrame([
            [line.split(': ')[0], line.split(': ')[1]] 
            for line in peak_hours_text if ':' in line
        ])
        
        fig.add_trace(
            go.Table(
                header=dict(
                    values=['Metric', 'Value'],
                    fill_color='paleturquoise',
                    align='left'
                ),
                cells=dict(
                    values=peak_hours_data.T.values,
                    fill_color='lavender',
                    align='left'
                )
            ),
            row=4, col=2
        )

        # Update layout
        fig.update_layout(
            height=1600,
            width=1600,
            title_text="BMRS Analysis Dashboard",
            showlegend=True,
            template='plotly_white'
        )

        return fig

    def save_analysis_dashboard(self, analysis_result: AnalysisResult,
                              prices_df: pd.DataFrame, volumes_df: pd.DataFrame,
                              filename: str = "bmrs_dashboard.html"):
        """Save the analysis dashboard to an HTML file"""
        dashboard = self.create_analysis_dashboard(analysis_result, prices_df, volumes_df)
        dashboard.write_html(filename, full_html=True, include_plotlyjs=True)
        return filename