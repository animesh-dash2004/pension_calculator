import pandas as pd
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

def get_compounding_frequency_value(frequency_str):
    """Maps string frequency to numerical value."""
    if frequency_str == "Daily":
        return 365
    elif frequency_str == "Monthly":
        return 12
    elif frequency_str == "Quarterly":
        return 4
    elif frequency_str == "Annually":
        return 1
    return 0  # Should not happen

def get_monthly_rate(annual_rate, compounding_frequency_value):
    """Calculates the effective monthly interest rate."""
    if compounding_frequency_value == 0:  # Avoid division by zero
        return 0.0
    if annual_rate == 0:  # If annual rate is 0, monthly rate is 0
        return 0.0

    # Calculate the effective annual rate
    effective_annual_rate = (1 + annual_rate / compounding_frequency_value)**compounding_frequency_value - 1
    
    # Convert effective annual rate to effective monthly rate
    monthly_rate = (1 + effective_annual_rate)**(1/12) - 1
    return monthly_rate

def format_currency(value):
    """Format a value as Indian Rupees."""
    return f"₹{value:,.2f}"

def format_percentage(value):
    """Format a value as a percentage."""
    return f"{value:.2f}%"

def format_date(dt):
    """Format a date in a user-friendly format."""
    if isinstance(dt, datetime):
        return dt.strftime('%B %Y')
    elif isinstance(dt, date):
        return dt.strftime('%B %Y')
    elif isinstance(dt, str):
        try:
            dt = datetime.strptime(dt, '%Y-%m')
            return dt.strftime('%B %Y')
        except:
            return dt
    return str(dt)

def get_date_range(start_date, end_date):
    """Generate a list of dates between start_date and end_date."""
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date)
        current_date += relativedelta(months=1)
    return dates