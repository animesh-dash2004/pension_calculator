# Dynamic Pension Fund Calculator

A modern, interactive application for comparing different pension schemes and making informed financial decisions.

## Features

- **Multi-scheme Comparison**: Compare two pension schemes (58 Years Old and 60 Years Old)
- **Dynamic Visualization**: Interactive charts showing the growth of each scheme over time
- **Detailed Analysis**: Monthly breakdowns of contributions, growth, and payouts
- **Tax Implications**: Optional tax calculations for pension income before age 60
- **Time Navigation**: Easily navigate through different time periods with back/forward buttons
- **Modern UI**: Clean, responsive interface with summary cards and detailed tables
- **Performance Analysis**: Automatically detect when one scheme overtakes another in value

## Getting Started

### Prerequisites

- Python 3.7+
- pip (Python package manager)

### Installation

1. Clone this repository or download the source code
2. Navigate to the project directory
3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Running the Application

```bash
streamlit run app.py
```

The application will open in your default web browser.

## Usage Guide

1. **Home Page**: Start by clicking the "Start Calculating" button on the home page
2. **Configure Parameters**: Use the sidebar to set your pension parameters:
   - General contribution details (lump sum, monthly contributions)
   - Scheme 58 parameters (pension amount, start date, growth rates)
   - Scheme 60 parameters (pension amount, start date, growth rates)
   - Tax settings (enable/disable tax calculations, set tax rate)
3. **Navigate Time**: Use the date navigation buttons to move forward or backward in time
4. **View Results**: Examine the summary cards, comparison chart, and detailed tables
5. **Analyze Performance**: See when one scheme overtakes another and which performs better overall

## Application Structure

The application is organized into modular components for better maintainability:

- **app.py**: Main application file with routing and page structure
- **calculations.py**: Core calculation logic for pension schemes
- **ui_components.py**: Reusable UI components and visualization functions
- **utils.py**: Helper functions for formatting and calculations

## Configuration Options

### General Parameters
- **Initial Lump Sum**: Starting amount for both schemes
- **Lump Sum Date**: When the initial amount is invested
- **Monthly Contribution**: Regular monthly contribution amount

### Scheme 58 Parameters
- **Pension Amount**: Monthly pension payment
- **Pension Start Date**: When pension payments begin
- **Contribution End Date**: When contributions to the provider stop
- **Reinvestment Rate**: Growth rate for reinvested pension income
- **SIP Fund Growth Rate**: Growth rate for the SIP fund

### Scheme 60 Parameters
- **Pension Amount**: Monthly pension payment
- **Pension Start Date**: When pension payments begin
- **Contribution End Date**: When contributions to the provider stop
- **Reinvestment Rate**: Growth rate for reinvested pension income

### Tax Settings
- **Enable Tax Implications**: Toggle tax calculations on/off
- **Tax Rate**: Percentage rate for tax calculations

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Data visualization using [Plotly](https://plotly.com/)
- Data manipulation with [Pandas](https://pandas.pydata.org/)
