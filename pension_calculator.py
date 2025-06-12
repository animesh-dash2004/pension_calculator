import streamlit as st
import pandas as pd
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="Dynamic Pension Fund Calculator", layout="wide")

st.title("Dynamic Pension Fund Calculator")

# --- Helper Functions ---
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
    return 0 # Should not happen

def get_monthly_rate(annual_rate, compounding_frequency_value):
    """Calculates the effective monthly interest rate."""
    if compounding_frequency_value == 0 or annual_rate == 0:
        return 0.0

    # Avoid division by zero if annual_rate is huge or compounding_frequency_value is small
    # but the primary safeguard is compounding_frequency_value == 0
    
    # Calculate the effective annual rate
    effective_annual_rate = (1 + annual_rate / compounding_frequency_value)**compounding_frequency_value - 1
    
    # Convert effective annual rate to effective monthly rate
    monthly_rate = (1 + effective_annual_rate)**(1/12) - 1
    return monthly_rate

# --- Sidebar for User Inputs ---
st.sidebar.header("Configure Pension Parameters")

st.sidebar.subheader("General Contributions")
initial_lump_sum = st.sidebar.number_input("Initial Lump Sum (₹)", value=5500000.00, min_value=0.0, step=10000.0)
lump_sum_date = st.sidebar.date_input("Lump Sum Date", value=date(2025, 3, 1))

monthly_contribution = st.sidebar.number_input("Monthly Contribution (₹)", value=30000.00, min_value=0.0, step=1000.0)
contribution_start_date = st.sidebar.date_input("Contribution Start Date", value=date(2025, 4, 1))
contribution_end_date = st.sidebar.date_input("Contribution End Date", value=date(2028, 5, 1))


st.sidebar.subheader("Scheme 1 Parameters")
s1_pension_amount = st.sidebar.number_input("Scheme 1: Monthly Pension (₹)", value=85000.00, min_value=0.0, step=1000.0)
s1_pension_start_date = st.sidebar.date_input("Scheme 1: Pension Start Date", value=date(2026, 6, 1))
s1_reinvestment_rate = st.sidebar.number_input("Scheme 1: Reinvestment Annual Rate (%)", value=7.0, min_value=0.0, max_value=100.0, step=0.1) / 100
s1_reinvestment_compounding_freq_str = st.sidebar.selectbox("Scheme 1: Reinvestment Compounding", ["Monthly", "Quarterly", "Annually", "Daily"], index=1, key="s1_compounding")
s1_reinvestment_compounding_frequency = get_compounding_frequency_value(s1_reinvestment_compounding_freq_str)

st.sidebar.subheader("Scheme 2 Parameters")
s2_pension_amount = st.sidebar.number_input("Scheme 2: Monthly Pension (₹)", value=127000.00, min_value=0.0, step=1000.0)
s2_pension_start_date = st.sidebar.date_input("Scheme 2: Pension Start Date", value=date(2028, 6, 1))
s2_reinvestment_rate = st.sidebar.number_input("Scheme 2: Reinvestment Annual Rate (%)", value=7.0, min_value=0.0, max_value=100.0, step=0.1) / 100
s2_reinvestment_compounding_freq_str = st.sidebar.selectbox("Scheme 2: Reinvestment Compounding", ["Monthly", "Quarterly", "Annually", "Daily"], index=1, key="s2_compounding")
s2_reinvestment_compounding_frequency = get_compounding_frequency_value(s2_reinvestment_compounding_freq_str)

st.sidebar.subheader("Scheme 3 Parameters")
s3_growth_rate_phase1 = st.sidebar.number_input("Scheme 3: Growth Annual Rate (Phase 1, %) (until transition date)", value=8.3, min_value=0.0, max_value=100.0, step=0.1) / 100
s3_compounding_freq_phase1_str = st.sidebar.selectbox("Scheme 3: Compounding Phase 1", ["Monthly", "Quarterly", "Annually", "Daily"], index=0, key="s3_compounding_phase1")
s3_compounding_frequency_phase1 = get_compounding_frequency_value(s3_compounding_freq_phase1_str)
s3_transition_date = st.sidebar.date_input("Scheme 3: Phase 1 End Date (Transition to Phase 2)", value=date(2028, 5, 31)) # End of May 2028 for original logic

s3_growth_rate_phase2 = st.sidebar.number_input("Scheme 3: Growth Annual Rate (Phase 2, %) (from transition date)", value=7.0, min_value=0.0, max_value=100.0, step=0.1) / 100
s3_compounding_freq_phase2_str = st.sidebar.selectbox("Scheme 3: Compounding Phase 2", ["Monthly", "Quarterly", "Annually", "Daily"], index=1, key="s3_compounding_phase2")
s3_compounding_frequency_phase2 = get_compounding_frequency_value(s3_compounding_freq_phase2_str)

# --- Calculation Logic --- (Updated to use dynamic inputs)
def calculate_scheme1(end_date, initial_lump_sum_val, lump_sum_date_val, monthly_contribution_val,
                      contribution_start_date_val, contribution_end_date_val,
                      pension_amount_s1, pension_start_date_s1, reinvestment_rate_s1, reinvestment_compounding_frequency_s1):
    records = []
    contributions_paid = 0.0
    pension_reinvestment_balance = 0.0
    pension_reinvestment_interest_earned = 0.0

    # Ensure current_date is datetime object for comparison with other datetime objects
    current_date = datetime(lump_sum_date_val.year, lump_sum_date_val.month, 1)
    end_date_dt = datetime(end_date.year, end_date.month, 1)

    monthly_reinvestment_rate_s1 = get_monthly_rate(reinvestment_rate_s1, reinvestment_compounding_frequency_s1)

    while current_date <= end_date_dt:
        added_to_contributions_this_month = 0.0
        pension_received_this_month = 0.0
        interest_on_pension_reinvestment = 0.0

        if current_date == datetime(lump_sum_date_val.year, lump_sum_date_val.month, 1):
            contributions_paid += initial_lump_sum_val
            added_to_contributions_this_month += initial_lump_sum_val

        # Using 1st day of month for date comparisons to align with current_date
        contrib_start_dt = datetime(contribution_start_date_val.year, contribution_start_date_val.month, 1)
        contrib_end_dt = datetime(contribution_end_date_val.year, contribution_end_date_val.month, 1)
        if contrib_start_dt <= current_date <= contrib_end_dt:
            contributions_paid += monthly_contribution_val
            added_to_contributions_this_month += monthly_contribution_val

        pension_start_dt_s1 = datetime(pension_start_date_s1.year, pension_start_date_s1.month, 1)
        if current_date >= pension_start_dt_s1:
            pension_received_this_month = pension_amount_s1
            pension_reinvestment_balance += pension_received_this_month

        if pension_reinvestment_balance > 0:
            interest_on_pension_reinvestment = pension_reinvestment_balance * monthly_reinvestment_rate_s1
            pension_reinvestment_balance += interest_on_pension_reinvestment
            pension_reinvestment_interest_earned += interest_on_pension_reinvestment

        records.append({
            'Date': current_date.strftime('%Y-%m'),
            'Contributions Paid This Month': added_to_contributions_this_month,
            'Cumulative Contributions Paid': contributions_paid,
            'Pension Received': pension_received_this_month,
            'Interest on Reinvestment': interest_on_pension_reinvestment,
            'Pension Reinvestment Pot': pension_reinvestment_balance,
            'Total Value': pension_reinvestment_balance
        })

        current_date += relativedelta(months=1)

    return records, pension_reinvestment_interest_earned, pension_reinvestment_balance

def calculate_scheme2(end_date, initial_lump_sum_val, lump_sum_date_val, monthly_contribution_val,
                      contribution_start_date_val, contribution_end_date_val,
                      pension_amount_s2, pension_start_date_s2, reinvestment_rate_s2, reinvestment_compounding_frequency_s2):
    records = []
    contributions_paid = 0.0
    pension_reinvestment_balance = 0.0
    pension_reinvestment_interest_earned = 0.0

    current_date = datetime(lump_sum_date_val.year, lump_sum_date_val.month, 1)
    end_date_dt = datetime(end_date.year, end_date.month, 1)

    monthly_reinvestment_rate_s2 = get_monthly_rate(reinvestment_rate_s2, reinvestment_compounding_frequency_s2)

    while current_date <= end_date_dt:
        added_to_contributions_this_month = 0.0
        pension_received_this_month = 0.0
        interest_on_pension_reinvestment = 0.0

        if current_date == datetime(lump_sum_date_val.year, lump_sum_date_val.month, 1):
            contributions_paid += initial_lump_sum_val
            added_to_contributions_this_month += initial_lump_sum_val

        contrib_start_dt = datetime(contribution_start_date_val.year, contribution_start_date_val.month, 1)
        contrib_end_dt = datetime(contribution_end_date_val.year, contribution_end_date_val.month, 1)
        if contrib_start_dt <= current_date <= contrib_end_dt:
            contributions_paid += monthly_contribution_val
            added_to_contributions_this_month += monthly_contribution_val

        pension_start_dt_s2 = datetime(pension_start_date_s2.year, pension_start_date_s2.month, 1)
        if current_date >= pension_start_dt_s2:
            pension_received_this_month = pension_amount_s2
            pension_reinvestment_balance += pension_received_this_month

        if pension_reinvestment_balance > 0:
            interest_on_pension_reinvestment = pension_reinvestment_balance * monthly_reinvestment_rate_s2
            pension_reinvestment_balance += interest_on_pension_reinvestment
            pension_reinvestment_interest_earned += interest_on_pension_reinvestment

        records.append({
            'Date': current_date.strftime('%Y-%m'),
            'Contributions Paid This Month': added_to_contributions_this_month,
            'Cumulative Contributions Paid': contributions_paid,
            'Pension Received': pension_received_this_month,
            'Interest on Reinvestment': interest_on_pension_reinvestment,
            'Pension Reinvestment Pot': pension_reinvestment_balance,
            'Total Value': pension_reinvestment_balance
        })
        current_date += relativedelta(months=1)

    return records, pension_reinvestment_interest_earned, pension_reinvestment_balance

def calculate_scheme3(end_date, initial_lump_sum_val, lump_sum_date_val, monthly_contribution_val,
                      contribution_start_date_val, contribution_end_date_val,
                      growth_rate_phase1_s3, compounding_frequency_phase1_s3, transition_date_s3,
                      growth_rate_phase2_s3, compounding_frequency_phase2_s3):
    records = []
    balance = 0.0
    total_interest_earned = 0.0

    current_date = datetime(lump_sum_date_val.year, lump_sum_date_val.month, 1)
    end_date_dt = datetime(end_date.year, end_date.month, 1)
    
    # Convert transition_date to datetime object for comparison
    transition_date_dt = datetime(transition_date_s3.year, transition_date_s3.month, transition_date_s3.day)


    while current_date <= end_date_dt:
        month_start_balance = balance
        added_amount_this_month = 0.0
        interest_this_month = 0.0

        if current_date == datetime(lump_sum_date_val.year, lump_sum_date_val.month, 1):
            balance += initial_lump_sum_val
            added_amount_this_month += initial_lump_sum_val

        contrib_start_dt = datetime(contribution_start_date_val.year, contribution_start_date_val.month, 1)
        contrib_end_dt = datetime(contribution_end_date_val.year, contribution_end_date_val.month, 1)
        if contrib_start_dt <= current_date <= contrib_end_dt:
            balance += monthly_contribution_val
            added_amount_this_month += monthly_contribution_val

        # Determine applicable interest rate and compounding for the current month
        # Note: current_date is 1st of the month, transition_date_dt could be any day.
        # We need to decide if the *month* of current_date falls into phase 1 or phase 2.
        # If transition_date_dt is e.g., May 31, 2028, then May 2028 is phase 1, June 2028 is phase 2.
        if current_date <= transition_date_dt.replace(day=1): # If current month is before or same as transition month
            monthly_rate = get_monthly_rate(growth_rate_phase1_s3, compounding_frequency_phase1_s3)
        else: # Current month is after the transition month
            monthly_rate = get_monthly_rate(growth_rate_phase2_s3, compounding_frequency_phase2_s3)
        
        interest_this_month = balance * monthly_rate
        balance += interest_this_month
        total_interest_earned += interest_this_month

        records.append({
            'Date': current_date.strftime('%Y-%m'),
            'Start Balance': month_start_balance,
            'Added Amount': added_amount_this_month,
            'Interest Earned': interest_this_month,
            'End Balance': balance,
            'Total Value': balance
        })

        current_date += relativedelta(months=1)

    return records, total_interest_earned, balance

def analyze_scheme_performance(s1_records, s2_records, s3_records):
    # Convert records to DataFrames for easier manipulation
    df1 = pd.DataFrame(s1_records)[['Date', 'Total Value']].rename(columns={'Total Value': 'Scheme 1 Value'})
    df2 = pd.DataFrame(s2_records)[['Date', 'Total Value']].rename(columns={'Total Value': 'Scheme 2 Value'})
    df3 = pd.DataFrame(s3_records)[['Date', 'Total Value']].rename(columns={'Total Value': 'Scheme 3 Value'})

    # Merge dataframes on 'Date'
    combined_df = df1.merge(df2, on='Date', how='outer').merge(df3, on='Date', how='outer').fillna(0)
    combined_df['Date'] = pd.to_datetime(combined_df['Date'])
    combined_df = combined_df.sort_values('Date').reset_index(drop=True)

    overtakes = []
    
    if combined_df.empty:
        return [], [] # No data to analyze

    # Initialize previous values to the first month's values
    prev_s1 = combined_df['Scheme 1 Value'].iloc[0]
    prev_s2 = combined_df['Scheme 2 Value'].iloc[0]
    prev_s3 = combined_df['Scheme 3 Value'].iloc[0]

    for i in range(1, len(combined_df)):
        current_date = combined_df['Date'].iloc[i]
        s1_val = combined_df['Scheme 1 Value'].iloc[i]
        s2_val = combined_df['Scheme 2 Value'].iloc[i]
        s3_val = combined_df['Scheme 3 Value'].iloc[i]

        # Check for overtakes
        # Scheme 1 overtakes Scheme 2
        if s1_val > s2_val and prev_s1 <= prev_s2 and s1_val > 0 and s2_val > 0: # Check > 0 to avoid false positives at start
            overtakes.append(f"Scheme 1 overtakes Scheme 2 on {current_date.strftime('%Y-%m')}")
        # Scheme 1 overtakes Scheme 3
        if s1_val > s3_val and prev_s1 <= prev_s3 and s1_val > 0 and s3_val > 0:
            overtakes.append(f"Scheme 1 overtakes Scheme 3 on {current_date.strftime('%Y-%m')}")
        
        # Scheme 2 overtakes Scheme 1
        if s2_val > s1_val and prev_s2 <= prev_s1 and s2_val > 0 and s1_val > 0:
            overtakes.append(f"Scheme 2 overtakes Scheme 1 on {current_date.strftime('%Y-%m')}")
        # Scheme 2 overtakes Scheme 3
        if s2_val > s3_val and prev_s2 <= prev_s3 and s2_val > 0 and s3_val > 0:
            overtakes.append(f"Scheme 2 overtakes Scheme 3 on {current_date.strftime('%Y-%m')}")

        # Scheme 3 overtakes Scheme 1
        if s3_val > s1_val and prev_s3 <= prev_s1 and s3_val > 0 and s1_val > 0:
            overtakes.append(f"Scheme 3 overtakes Scheme 1 on {current_date.strftime('%Y-%m')}")
        # Scheme 3 overtakes Scheme 2
        if s3_val > s2_val and prev_s3 <= prev_s2 and s3_val > 0 and s2_val > 0:
            overtakes.append(f"Scheme 3 overtakes Scheme 2 on {current_date.strftime('%Y-%m')}")

        # Update previous values for the next iteration
        prev_s1 = s1_val
        prev_s2 = s2_val
        prev_s3 = s3_val
    
    # Determine current ranking
    if not combined_df.empty:
        final_values = {
            'Scheme 1': combined_df['Scheme 1 Value'].iloc[-1],
            'Scheme 2': combined_df['Scheme 2 Value'].iloc[-1],
            'Scheme 3': combined_df['Scheme 3 Value'].iloc[-1]
        }
        sorted_schemes = sorted(final_values.items(), key=lambda item: item[1], reverse=True)
        ranking = [f"{i+1}. {scheme_name} (₹{value:,.2f})" for i, (scheme_name, value) in enumerate(sorted_schemes)]
    else:
        ranking = ["No data to determine ranking."]

    return overtakes, ranking

# --- Streamlit UI ---
# Set initial display end date based on user inputs
initial_display_end_date_calc = max(
    datetime(contribution_end_date.year, contribution_end_date.month, 1),
    datetime(s1_pension_start_date.year, s1_pension_start_date.month, 1),
    datetime(s2_pension_start_date.year, s2_pension_start_date.month, 1)
) + relativedelta(months=2) # Add a couple of months to see initial pension impact

if 'current_display_end_date' not in st.session_state:
    st.session_state.current_display_end_date = initial_display_end_date_calc

# Recalculate initial display end date if input dates change
# This ensures the default view adjusts to new configurations
if (st.session_state.current_display_end_date < initial_display_end_date_calc) or \
   (st.session_state.current_display_end_date.year == datetime.now().year and st.session_state.current_display_end_date.month == datetime.now().month):
    st.session_state.current_display_end_date = initial_display_end_date_calc

if st.button("Calculate for Next Year"):
    st.session_state.current_display_end_date += relativedelta(years=1)

st.markdown(f"### Calculations up to: {st.session_state.current_display_end_date.strftime('%B %Y')}")

# Calculate and display schemes using dynamic inputs
s1_records, s1_interest, s1_final_value = calculate_scheme1(
    st.session_state.current_display_end_date, initial_lump_sum, lump_sum_date, monthly_contribution,
    contribution_start_date, contribution_end_date,
    s1_pension_amount, s1_pension_start_date, s1_reinvestment_rate, s1_reinvestment_compounding_frequency
)
s2_records, s2_interest, s2_final_value = calculate_scheme2(
    st.session_state.current_display_end_date, initial_lump_sum, lump_sum_date, monthly_contribution,
    contribution_start_date, contribution_end_date,
    s2_pension_amount, s2_pension_start_date, s2_reinvestment_rate, s2_reinvestment_compounding_frequency
)
s3_records, s3_interest, s3_final_value = calculate_scheme3(
    st.session_state.current_display_end_date, initial_lump_sum, lump_sum_date, monthly_contribution,
    contribution_start_date, contribution_end_date,
    s3_growth_rate_phase1, s3_compounding_frequency_phase1, s3_transition_date,
    s3_growth_rate_phase2, s3_compounding_frequency_phase2
)

st.header("Scheme Comparison Summary")
summary_data = {
    'Scheme': ['Scheme 1', 'Scheme 2', 'Scheme 3'],
    'Total Value at End Date': [f"₹{s1_final_value:,.2f}", f"₹{s2_final_value:,.2f}", f"₹{s3_final_value:,.2f}"],
    'Total Interest Earned': [f"₹{s1_interest:,.2f}", f"₹{s2_interest:,.2f}", f"₹{s3_interest:,.2f}"]
}
summary_df = pd.DataFrame(summary_data)
st.table(summary_df)

st.header("Performance Analysis")
overtakes, ranking = analyze_scheme_performance(s1_records, s2_records, s3_records)

if overtakes:
    st.subheader("Scheme Overtakes:")
    for overtake_info in overtakes:
        st.write(f"- {overtake_info}")
else:
    st.write("No overtakes detected so far for the displayed period.")

st.subheader("Current Ranking:")
for rank_info in ranking:
    st.write(f"- {rank_info}")


# Detailed Tables
st.header("Detailed Monthly Breakdown")

# Scheme 1 Details
st.subheader("Scheme 1 Details")
if s1_records:
    s1_df = pd.DataFrame(s1_records)
    st.dataframe(s1_df[['Date', 'Contributions Paid This Month', 'Cumulative Contributions Paid', 'Pension Received', 'Interest on Reinvestment', 'Pension Reinvestment Pot', 'Total Value']].style.format({
        'Contributions Paid This Month': "₹{:,.2f}",
        'Cumulative Contributions Paid': "₹{:,.2f}",
        'Pension Received': "₹{:,.2f}",
        'Interest on Reinvestment': "₹{:,.2f}",
        'Pension Reinvestment Pot': "₹{:,.2f}",
        'Total Value': "₹{:,.2f}"
    }), height=300)
else:
    st.write("No data to display for Scheme 1 for the selected period.")

# Scheme 2 Details
st.subheader("Scheme 2 Details")
if s2_records:
    s2_df = pd.DataFrame(s2_records)
    st.dataframe(s2_df[['Date', 'Contributions Paid This Month', 'Cumulative Contributions Paid', 'Pension Received', 'Interest on Reinvestment', 'Pension Reinvestment Pot', 'Total Value']].style.format({
        'Contributions Paid This Month': "₹{:,.2f}",
        'Cumulative Contributions Paid': "₹{:,.2f}",
        'Pension Received': "₹{:,.2f}",
        'Interest on Reinvestment': "₹{:,.2f}",
        'Pension Reinvestment Pot': "₹{:,.2f}",
        'Total Value': "₹{:,.2f}"
    }), height=300)
else:
    st.write("No data to display for Scheme 2 for the selected period.")

# Scheme 3 Details
st.subheader("Scheme 3 Details")
if s3_records:
    s3_df = pd.DataFrame(s3_records)
    st.dataframe(s3_df[['Date', 'Start Balance', 'Added Amount', 'Interest Earned', 'End Balance', 'Total Value']].style.format({
        'Start Balance': "₹{:,.2f}",
        'Added Amount': "₹{:,.2f}",
        'Interest Earned': "₹{:,.2f}",
        'End Balance': "₹{:,.2f}",
        'Total Value': "₹{:,.2f}"
    }), height=300)
else:
    st.write("No data to display for Scheme 3 for the selected period.")

# To run this: streamlit run your_script_name.py