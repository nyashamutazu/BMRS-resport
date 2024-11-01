# BMRS Imbalance Analysis Tool

## Overview

A comprehensive tool for analysing BMRS (Balancing Mechanism Reporting Service) imbalance prices and volumes. This project provides functionality to fetch, process, analyse, and visualise imbalance data from the BMRS API.

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [API Documentation](#api-documentation)
- [Visualisation Dashboard](#visualisation-dashboard)
- [Testing](#testing)

## Features

- **Data Retrieval**: Automated fetching of imbalance prices and volumes from BMRS API
- **Data Processing**: Cleaning and structuring of raw data into time series
- **Analysis Capabilities**:
  - Half-hourly time series analysis
  - Daily imbalance cost calculations
  - Peak volume identification
  - Statistical analysis and patterns
- **Visualisation**:
  - Interactive dashboard for data exploration
  - Multiple chart types and views
  - Responsive design for all devices

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd bmrs_project
```

2. Create and activate virtual environment:

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

```bash
cp .env.example .env
# Edit .env file with your BMRS API key
```

## Configuration

### Required API Access

- BMRS API key (obtain from ELEXON Portal)
- API rate limits: 10 requests/second
- Data availability: Rolling 24 months

## Usage Examples

### Basic Data Retrieval

```python
from api.bmrs import BMRSApi

# Initialise API
api = BMRSApi()

# Get data for a specific date
data = api.get_imbalance_data('2024-03-01')

# Get historic data
historic_data = api.get_historic_imbalance_data('2024-03-01', '2024-03-07')
```

### Data Processing and Analysis

```python
from utils.data_processor import BMRSDataProcessor
from utils.imbalance_analysis import ImbalanceAnalysis
from utils.volume_analysis import VolumeAnalysis

# Process raw data
prices_df, volumes_df = BMRSDataProcessor.clean_and_process_data(raw_data)

# Analyse imbalance costs
daily_metrics = ImbalanceAnalysis.calculate_daily_imbalance_metrics(prices_df, volumes_df)
daily_report = ImbalanceAnalysis.generate_daily_report(daily_metrics, '2024-03-01')

# Analyse volumes
hourly_stats, peak_hours_report = VolumeAnalysis.analyse_hourly_volumes(volumes_df)
```

## API Documentation

### BMRSApi

- `get_imbalance_data(settlement_date, settlement_period=None)`
  - Parameters:
    - settlement_date (str): Date in 'YYYY-MM-DD' format
    - settlement_period (int, optional): Specific period (1-48)
  - Returns: DataFrame with imbalance data

### DataProcessor

- `clean_and_process_data(df)`
  - Parameters:
    - df (DataFrame): Raw BMRS data
  - Returns: Tuple of (prices_df, volumes_df)

### ImbalanceAnalysis

- `calculate_daily_imbalance_metrics(prices_df, volumes_df)`
  - Parameters:
    - prices_df (DataFrame): Processed prices data
    - volumes_df (DataFrame): Processed volumes data
  - Returns: DataFrame with daily metrics

### Features

- Hourly volume patterns
- Price trends analysis
- Volume distribution
- Interactive filtering
- Responsive design

### Visualisation

## Testing

Run tests:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_bmrs_caller.py

# Run with coverage
pytest --cov=src tests/
```
