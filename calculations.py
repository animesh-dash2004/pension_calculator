import pandas as pd
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from utils import get_compounding_frequency_value, get_monthly_rate

def calculate_scheme1_logic(end_date, initial_lump_sum_val, lump_sum_date_val, monthly_contribution_val,
                          s1_contribution_to_provider_end_date_val, s1_pension_amount, s1_pension_start_date,
                          s1_reinvestment_rate, s1_reinvestment_compounding_frequency,
                          s1_sip_fund_growth_rate, s1_sip_fund_compounding_frequency,
                          s2_pension_start_date, # This is the user's 60th birthday for tax purposes
                          enable_tax, tax_rate
                         ):
    """
    Calculate the financial outcomes for Pension Scheme 58 Years Old.
    
    This scheme's calculation involves several distinct phases and pots:
    - Contributions Paid (Outflow): Initial Lump Sum and Monthly Contributions until 'Scheme 58: Contribution to Provider End Date'
    - Pension Received (Inflow): From 'Scheme 58: Pension Start Date', the monthly pension is received
    - Separate SIP Fund: After contribution end until Scheme 60 start date, contributions go to SIP fund
    - SIP Fund Merger: At Scheme 60 start date, SIP fund transfers to Pension Reinvestment Pot
    - Pension Reinvestment Pot: Holds received pension and grows at the specified rate
    """
    records = []
    
    cumulative_contributions_paid_to_provider = 0.0
    
    pension_reinvestment_pot_s1 = 0.0 
    pension_reinvestment_interest_earned_s1 = 0.0 # Tracks net interest earned

    sip_fund_balance_s1 = 0.0
    sip_fund_interest_earned_s1 = 0.0 # Tracks interest earned on SIP fund (no tax)
    
    # Tax tracking
    total_tax_paid_on_pension = 0.0
    total_tax_paid_on_reinvestment_interest = 0.0

    current_date = datetime(lump_sum_date_val.year, lump_sum_date_val.month, 1)
    end_date_dt = datetime(end_date.year, end_date.month, 1)

    lump_sum_dt = datetime(lump_sum_date_val.year, lump_sum_date_val.month, 1)
    s1_contrib_end_dt = datetime(s1_contribution_to_provider_end_date_val.year, s1_contribution_to_provider_end_date_val.month, 1)
    s1_pension_start_dt = datetime(s1_pension_start_date.year, s1_pension_start_date.month, 1)
    s2_pension_start_dt = datetime(s2_pension_start_date.year, s2_pension_start_date.month, 1) # User turns 60 here

    monthly_sip_rate_s1 = get_monthly_rate(s1_sip_fund_growth_rate, s1_sip_fund_compounding_frequency)
    monthly_reinvestment_rate_s1 = get_monthly_rate(s1_reinvestment_rate, s1_reinvestment_compounding_frequency)

    while current_date <= end_date_dt:
        # Values for the current month
        contribution_paid_this_month = 0.0
        pension_received_this_month_gross = 0.0
        pension_received_this_month_net = 0.0
        tax_on_pension_this_month = 0.0
        interest_earned_on_reinvestment_gross = 0.0
        interest_earned_on_reinvestment_net = 0.0
        tax_on_reinvestment_interest_this_month = 0.0
        interest_earned_on_sip_fund = 0.0 # SIP fund is not taxed
        added_to_sip_fund_this_month = 0.0 # Monthly SIP contribution amount

        # 1. Handle Lump Sum Payment (outflow)
        if current_date == lump_sum_dt:
            cumulative_contributions_paid_to_provider += initial_lump_sum_val
            contribution_paid_this_month += initial_lump_sum_val

        # 2. Handle Monthly Contributions (outflow to provider or inflow to SIP)
        if current_date <= s1_contrib_end_dt:
            cumulative_contributions_paid_to_provider += monthly_contribution_val
            contribution_paid_this_month += monthly_contribution_val
        elif s1_contrib_end_dt < current_date < s2_pension_start_dt:
            # Monthly SIP contribution
            sip_fund_balance_s1 += monthly_contribution_val 
            added_to_sip_fund_this_month += monthly_contribution_val
            
            # Interest on SIP fund (not taxed)
            current_sip_interest = sip_fund_balance_s1 * monthly_sip_rate_s1
            sip_fund_balance_s1 += current_sip_interest
            sip_fund_interest_earned_s1 += current_sip_interest
            interest_earned_on_sip_fund = current_sip_interest

        # 3. Handle Pension Payouts (inflow to reinvestment pot)
        if current_date >= s1_pension_start_dt:
            pension_received_this_month_gross = s1_pension_amount
            
            if enable_tax and current_date < s2_pension_start_dt: # Tax applies before 60
                tax_on_pension_this_month = pension_received_this_month_gross * tax_rate
                pension_received_this_month_net = pension_received_this_month_gross - tax_on_pension_this_month
            else: # No tax at or after 60
                tax_on_pension_this_month = 0.0
                pension_received_this_month_net = pension_received_this_month_gross
            
            pension_reinvestment_pot_s1 += pension_received_this_month_net # Add net pension to pot
            total_tax_paid_on_pension += tax_on_pension_this_month

        # 4. Handle SIP Fund Merger into Pension Reinvestment Pot
        if current_date == s2_pension_start_dt:
            pension_reinvestment_pot_s1 += sip_fund_balance_s1
            sip_fund_balance_s1 = 0 # Reset SIP fund after transfer

        # 5. Handle Reinvestment Growth on Pension Reinvestment Pot
        # This calculation needs to happen AFTER all inflows for the month
        # The condition `pension_reinvestment_pot_s1 > 0` is still good to prevent 0*rate interest
        if pension_reinvestment_pot_s1 > 0: 
            current_reinvestment_interest_gross = pension_reinvestment_pot_s1 * monthly_reinvestment_rate_s1
            
            if enable_tax and current_date < s2_pension_start_dt: # Tax applies before 60
                tax_on_reinvestment_interest_this_month = current_reinvestment_interest_gross * tax_rate
                interest_earned_on_reinvestment_net = current_reinvestment_interest_gross - tax_on_reinvestment_interest_this_month
            else: # No tax at or after 60
                tax_on_reinvestment_interest_this_month = 0.0
                interest_earned_on_reinvestment_net = current_reinvestment_interest_gross
            
            pension_reinvestment_pot_s1 += interest_earned_on_reinvestment_net # Add net interest to pot
            pension_reinvestment_interest_earned_s1 += interest_earned_on_reinvestment_net # Track net interest
            total_tax_paid_on_reinvestment_interest += tax_on_reinvestment_interest_this_month
        
        current_total_value = pension_reinvestment_pot_s1 + sip_fund_balance_s1 # Both pots count towards user's total

        records.append({
            'Date': current_date.strftime('%Y-%m'),
            'Contributions Paid This Month': contribution_paid_this_month,
            'Cumulative Contributions Paid (Outflow)': cumulative_contributions_paid_to_provider,
            'Pension Received This Month (Gross)': pension_received_this_month_gross,
            'Tax on Pension This Month': tax_on_pension_this_month,
            'Pension Received This Month (Net)': pension_received_this_month_net,
            'Monthly SIP Contribution': added_to_sip_fund_this_month,
            'Interest on Separate SIP Fund': interest_earned_on_sip_fund, # Not taxed
            'Separate SIP Fund Balance': sip_fund_balance_s1,
            'Interest on Pension Reinvestment (Gross)': interest_earned_on_reinvestment_gross,
            'Tax on Reinvestment Interest This Month': tax_on_reinvestment_interest_this_month,
            'Interest on Pension Reinvestment (Net)': interest_earned_on_reinvestment_net,
            'Pension Reinvestment Pot': pension_reinvestment_pot_s1,
            'Total Accumulated Value (User)': current_total_value
        })

        current_date += relativedelta(months=1)
    
    # Calculate overall total interest earned (net of tax for reinvestment pot, full for SIP)
    total_interest_earned_overall = pension_reinvestment_interest_earned_s1 + sip_fund_interest_earned_s1
    final_scheme_value_s1 = records[-1]['Total Accumulated Value (User)'] if records else 0.0

    return records, total_interest_earned_overall, final_scheme_value_s1, total_tax_paid_on_pension, total_tax_paid_on_reinvestment_interest

def calculate_scheme2_logic(end_date, initial_lump_sum_val, lump_sum_date_val, monthly_contribution_val,
                      s2_contribution_to_provider_end_date_val, s2_pension_amount, s2_pension_start_date,
                      s2_reinvestment_rate, s2_reinvestment_compounding_frequency):
    """
    Calculate the financial outcomes for Pension Scheme 60 Years Old.
    
    This scheme's calculation is simpler:
    - Contributions Paid (Outflow): Initial Lump Sum and Monthly Contributions until contribution end date
    - Pension Received (Inflow): From pension start date, the monthly pension is received
    - Pension Reinvestment Pot: Holds received pension and grows at the specified rate
    - No tax implications as pension starts at age 60
    """
    records = []
    
    cumulative_contributions_paid_to_provider = 0.0
    
    pension_reinvestment_pot_s2 = 0.0
    pension_reinvestment_interest_earned_s2 = 0.0 # Tracks net interest earned

    # No tax implications for Scheme 2 as pension starts at 60
    total_tax_paid_on_pension = 0.0
    total_tax_paid_on_reinvestment_interest = 0.0

    current_date = datetime(lump_sum_date_val.year, lump_sum_date_val.month, 1)
    end_date_dt = datetime(end_date.year, end_date.month, 1)

    lump_sum_dt = datetime(lump_sum_date_val.year, lump_sum_date_val.month, 1)
    s2_contrib_end_dt = datetime(s2_contribution_to_provider_end_date_val.year, s2_contribution_to_provider_end_date_val.month, 1)
    s2_pension_start_dt = datetime(s2_pension_start_date.year, s2_pension_start_date.month, 1)

    monthly_reinvestment_rate_s2 = get_monthly_rate(s2_reinvestment_rate, s2_reinvestment_compounding_frequency)

    while current_date <= end_date_dt:
        contribution_paid_this_month = 0.0
        pension_received_this_month_net = 0.0 # For S2, net is always gross (no tax)
        interest_on_pension_reinvestment_net = 0.0 # For S2, net is always gross (no tax)

        # 1. Handle Lump Sum Payment (outflow)
        if current_date == lump_sum_dt:
            cumulative_contributions_paid_to_provider += initial_lump_sum_val
            contribution_paid_this_month += initial_lump_sum_val

        # 2. Handle Monthly Contributions (outflow)
        if current_date <= s2_contrib_end_dt:
            cumulative_contributions_paid_to_provider += monthly_contribution_val
            contribution_paid_this_month += monthly_contribution_val

        # 3. Handle Pension Payouts (inflow to reinvestment pot) - No tax for S2
        if current_date >= s2_pension_start_dt:
            pension_received_this_month_net = s2_pension_amount # Full amount received
            pension_reinvestment_pot_s2 += pension_received_this_month_net

        # 4. Handle Reinvestment Growth on Pension Reinvestment Pot - No tax for S2
        # This calculation needs to happen AFTER all inflows for the month
        if pension_reinvestment_pot_s2 > 0: # Ensure there's a balance to earn interest
            interest_on_pension_reinvestment_net = pension_reinvestment_pot_s2 * monthly_reinvestment_rate_s2
            pension_reinvestment_pot_s2 += interest_on_pension_reinvestment_net
            pension_reinvestment_interest_earned_s2 += interest_on_pension_reinvestment_net

        records.append({
            'Date': current_date.strftime('%Y-%m'),
            'Contributions Paid This Month': contribution_paid_this_month,
            'Cumulative Contributions Paid (Outflow)': cumulative_contributions_paid_to_provider,
            'Pension Received This Month (Net)': pension_received_this_month_net,
            'Interest on Reinvestment (Net)': interest_on_pension_reinvestment_net,
            'Pension Reinvestment Pot': pension_reinvestment_pot_s2,
            'Total Accumulated Value (User)': pension_reinvestment_pot_s2
        })
        current_date += relativedelta(months=1)

    return records, pension_reinvestment_interest_earned_s2, pension_reinvestment_pot_s2, total_tax_paid_on_pension, total_tax_paid_on_reinvestment_interest

def analyze_scheme_performance(s1_records, s2_records):
    """
    Analyze and compare the performance of both pension schemes.
    
    Returns:
        - List of overtake events (when one scheme overtakes the other)
        - List of final rankings by value
    """
    # Convert records to DataFrames for easier manipulation
    df1 = pd.DataFrame(s1_records)[['Date', 'Total Accumulated Value (User)']].rename(columns={'Total Accumulated Value (User)': 'Pension Scheme 58 Years Old Value'})
    df2 = pd.DataFrame(s2_records)[['Date', 'Total Accumulated Value (User)']].rename(columns={'Total Accumulated Value (User)': 'Pension Scheme 60 Years Old Value'})

    # Merge dataframes on 'Date'
    combined_df = df1.merge(df2, on='Date', how='outer').fillna(0)
    combined_df['Date'] = pd.to_datetime(combined_df['Date'])
    combined_df = combined_df.sort_values('Date').reset_index(drop=True)

    overtakes = []
    
    if combined_df.empty:
        return [], [] # No data to analyze

    prev_s1 = 0
    prev_s2 = 0

    for i in range(len(combined_df)):
        current_date = combined_df['Date'].iloc[i]
        s1_val = combined_df['Pension Scheme 58 Years Old Value'].iloc[i]
        s2_val = combined_df['Pension Scheme 60 Years Old Value'].iloc[i]

        if s1_val > s2_val and prev_s1 <= prev_s2 and s1_val > 0:
            overtakes.append(f"Pension Scheme 58 Years Old overtakes Pension Scheme 60 Years Old on {current_date.strftime('%B %Y')}")
        
        if s2_val > s1_val and prev_s2 <= prev_s1 and s2_val > 0:
            overtakes.append(f"Pension Scheme 60 Years Old overtakes Pension Scheme 58 Years Old on {current_date.strftime('%B %Y')}")

        prev_s1 = s1_val
        prev_s2 = s2_val
    
    if not combined_df.empty:
        final_values = {
            'Pension Scheme 58 Years Old': combined_df['Pension Scheme 58 Years Old Value'].iloc[-1],
            'Pension Scheme 60 Years Old': combined_df['Pension Scheme 60 Years Old Value'].iloc[-1]
        }
        sorted_schemes = sorted(final_values.items(), key=lambda item: item[1], reverse=True)
        ranking = [f"{i+1}. {scheme_name} (₹{value:,.2f})" for i, (scheme_name, value) in enumerate(sorted_schemes)]
    else:
        ranking = ["No data to determine ranking."]

    return overtakes, ranking

def get_combined_dataframe(s1_records, s2_records):
    """
    Create a combined DataFrame for visualization purposes.
    """
    if not s1_records or not s2_records:
        return pd.DataFrame()
        
    df1 = pd.DataFrame(s1_records)[['Date', 'Total Accumulated Value (User)']].rename(columns={'Total Accumulated Value (User)': 'Scheme 58'})
    df2 = pd.DataFrame(s2_records)[['Date', 'Total Accumulated Value (User)']].rename(columns={'Total Accumulated Value (User)': 'Scheme 60'})
    
    combined_df = df1.merge(df2, on='Date', how='outer').fillna(0)
    combined_df['Date'] = pd.to_datetime(combined_df['Date'])
    combined_df = combined_df.sort_values('Date').reset_index(drop=True)
    
    return combined_df