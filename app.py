import streamlit as st
import pandas as pd
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from utils import get_compounding_frequency_value, format_currency, format_date
from calculations import (
    calculate_scheme1_logic, 
    calculate_scheme2_logic, 
    analyze_scheme_performance,
    get_combined_dataframe
)
from ui_components import (
    create_header,
    create_sidebar_inputs,
    create_date_navigation,
    create_scheme_comparison_chart,
    create_summary_cards,
    display_overtakes_and_ranking,
    create_scheme_details_tabs
)

# Configure the Streamlit page
st.set_page_config(
    page_title="Pension Calculator",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply global styling
st.markdown("""
<style>
    /* Global button styling */
    div.stButton > button {
        background-color: #FF4B4B;
        color: white !important;
        font-weight: bold;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1rem;
    }
    div.stButton > button:hover {
        background-color: #D03434;
        color: white !important;
    }
    
    /* Make sure text is visible on all buttons */
    div.stButton > button:focus {
        color: white !important;
    }
    
    /* Improve tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 10px 16px;
        border-radius: 4px 4px 0 0;
    }
    
    /* Improve overall spacing */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables if they don't exist
if 'page' not in st.session_state:
    st.session_state.page = 'home'

if 'current_display_end_date' not in st.session_state:
    # Default to 2 years after the latest pension start date
    today = date.today()
    st.session_state.current_display_end_date = datetime(today.year + 5, today.month, 1)

def home_page():
    """Landing page with app introduction and navigation."""
    create_header("Dynamic Pension Fund Calculator", "Compare different pension schemes to make informed decisions")
    
    st.markdown("""
    Welcome to the Dynamic Pension Fund Calculator! This tool helps you compare different pension schemes 
    and understand their long-term financial implications.

    ### What This Calculator Does
    - Compare two pension schemes (58 Years Old and 60 Years Old)
    - Calculate growth of investments over time with compound interest
    - Account for tax implications before age 60
    - Visualize when one scheme overtakes another in value
    - Provide detailed monthly breakdowns of your pension growth

    ### How to Use This Calculator
    1. Configure your pension parameters in the sidebar
    2. View the comparison results and charts
    3. Navigate through time to see how your pension grows
    4. Explore detailed breakdowns for each scheme
    """)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Start Calculating", type="primary", key="start_button"):
            st.session_state.page = 'calculator'
            st.rerun()

def calculator_page():
    """Main calculator page with inputs, calculations, and results."""
    create_header("Dynamic Pension Fund Calculator", "Compare different pension schemes to make informed decisions")
    
    # Get user inputs from sidebar
    inputs = create_sidebar_inputs()
    
    # Extract inputs for easier reference
    initial_lump_sum = inputs['initial_lump_sum']
    lump_sum_date = inputs['lump_sum_date']
    monthly_contribution = inputs['monthly_contribution']
    
    s1_pension_amount = inputs['s1_pension_amount']
    s1_pension_start_date = inputs['s1_pension_start_date']
    s1_contribution_to_provider_end_date = inputs['s1_contribution_to_provider_end_date']
    s1_reinvestment_rate = inputs['s1_reinvestment_rate']
    s1_reinvestment_compounding_freq_str = inputs['s1_reinvestment_compounding_freq_str']
    s1_reinvestment_compounding_frequency = get_compounding_frequency_value(s1_reinvestment_compounding_freq_str)
    s1_sip_fund_growth_rate = inputs['s1_sip_fund_growth_rate']
    s1_sip_fund_compounding_freq_str = inputs['s1_sip_fund_compounding_freq_str']
    s1_sip_fund_compounding_frequency = get_compounding_frequency_value(s1_sip_fund_compounding_freq_str)
    
    s2_pension_amount = inputs['s2_pension_amount']
    s2_pension_start_date = inputs['s2_pension_start_date']
    s2_contribution_to_provider_end_date = inputs['s2_contribution_to_provider_end_date']
    s2_reinvestment_rate = inputs['s2_reinvestment_rate']
    s2_reinvestment_compounding_freq_str = inputs['s2_reinvestment_compounding_freq_str']
    s2_reinvestment_compounding_frequency = get_compounding_frequency_value(s2_reinvestment_compounding_freq_str)
    
    enable_tax_implications = inputs['enable_tax_implications']
    tax_rate = inputs['tax_rate']
    
    # Set minimum display date based on inputs
    min_display_date = max(
        datetime(lump_sum_date.year, lump_sum_date.month, 1),
        datetime(s1_pension_start_date.year, s1_pension_start_date.month, 1),
        datetime(s2_pension_start_date.year, s2_pension_start_date.month, 1)
    ) + relativedelta(months=1)
    
    # Set maximum possible display date (e.g., 30 years from now)
    max_possible_date = datetime.now() + relativedelta(years=30)
    
    # Ensure current display date is within valid range
    if st.session_state.current_display_end_date < min_display_date:
        st.session_state.current_display_end_date = min_display_date + relativedelta(years=2)
    
    # Create date navigation
    new_date = create_date_navigation(
        st.session_state.current_display_end_date,
        min_display_date,
        max_possible_date
    )
    
    # Update date if navigation buttons were clicked
    if new_date != st.session_state.current_display_end_date:
        st.session_state.current_display_end_date = new_date
        st.rerun()
    
    # Calculate scheme results
    s1_records, s1_total_interest, s1_final_value, s1_total_pension_tax, s1_total_reinvestment_tax = calculate_scheme1_logic(
        st.session_state.current_display_end_date,
        initial_lump_sum, lump_sum_date, monthly_contribution,
        s1_contribution_to_provider_end_date, s1_pension_amount, s1_pension_start_date,
        s1_reinvestment_rate, s1_reinvestment_compounding_frequency,
        s1_sip_fund_growth_rate, s1_sip_fund_compounding_frequency,
        s2_pension_start_date, # This is the user's 60th birthday for tax purposes
        enable_tax_implications, tax_rate
    )
    
    s2_records, s2_total_interest, s2_final_value, s2_total_pension_tax, s2_total_reinvestment_tax = calculate_scheme2_logic(
        st.session_state.current_display_end_date,
        initial_lump_sum, lump_sum_date, monthly_contribution,
        s2_contribution_to_provider_end_date, s2_pension_amount, s2_pension_start_date,
        s2_reinvestment_rate, s2_reinvestment_compounding_frequency
    )
    
    # Analyze scheme performance
    overtakes, ranking = analyze_scheme_performance(s1_records, s2_records)
    
    # Create combined dataframe for visualization
    combined_df = get_combined_dataframe(s1_records, s2_records)
    
    # Display summary cards
    create_summary_cards(
        s1_final_value, s2_final_value,
        s1_total_interest, s2_total_interest,
        s1_total_pension_tax, s2_total_pension_tax,
        s1_total_reinvestment_tax, s2_total_reinvestment_tax,
        enable_tax_implications
    )
    
    # Display comparison chart
    create_scheme_comparison_chart(combined_df)
    
    # Display overtakes and ranking
    display_overtakes_and_ranking(overtakes, ranking)
    
    # Display detailed scheme information in tabs
    create_scheme_details_tabs(pd.DataFrame(s1_records), pd.DataFrame(s2_records), enable_tax_implications)
    
    # Back to home button
    if st.button("← Back to Home"):
        st.session_state.page = 'home'
        st.rerun()

# Main app routing
if st.session_state.page == 'home':
    home_page()
elif st.session_state.page == 'calculator':
    calculator_page()

# Footer
st.markdown("---")
st.markdown(" 2025 Dynamic Pension Fund Calculator | Created with Streamlit")