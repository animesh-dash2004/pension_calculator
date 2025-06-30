import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from utils import format_currency, format_date

def create_header(title, subtitle=None):
    """Create a header with optional subtitle."""
    st.title(title)
    if subtitle:
        st.markdown(f"<h3 style='margin-top:-15px;'>{subtitle}</h3>", unsafe_allow_html=True)
    st.markdown("---")

def create_sidebar_inputs():
    """Create all sidebar inputs for the pension calculator."""
    st.sidebar.header("Configure Pension Parameters")
    
    with st.sidebar.expander("General Contributions", expanded=True):
        initial_lump_sum = st.number_input("Initial Lump Sum (₹)", value=5500000.00, min_value=0.0, step=10000.0, key="initial_lump_sum")
        lump_sum_date = st.date_input("Lump Sum Date", value=date(2025, 3, 1), key="lump_sum_date")
        monthly_contribution = st.number_input("Monthly Contribution (₹) (Paid to provider or SIP fund)", value=30000.00, min_value=0.0, step=1000.0, key="monthly_contribution")
    
    with st.sidebar.expander("Pension Scheme 58 Years Old", expanded=True):
        s1_pension_amount = st.number_input("Scheme 58: Monthly Pension Received (₹)", value=85000.00, min_value=0.0, step=1000.0, key="s1_pension_amount")
        s1_pension_start_date = st.date_input("Scheme 58: Pension Start Date", value=date(2026, 6, 1), key="s1_pension_start_date")
        s1_contribution_to_provider_end_date = st.date_input("Scheme 58: Contribution to Provider End Date", value=date(2026, 5, 31), key="s1_contribution_end_date")
        
        st.sidebar.markdown("**Pension Reinvestment Parameters (from Scheme 58 Pension Start)**")
        s1_reinvestment_rate = st.number_input("Scheme 58: Pension Reinvestment Annual Rate (%)", value=7.0, min_value=0.0, max_value=100.0, step=0.1, key="s1_reinvestment_rate") / 100
        s1_reinvestment_compounding_freq_str = st.selectbox("Scheme 58: Pension Reinvestment Compounding", ["Monthly", "Quarterly", "Annually", "Daily"], index=1, key="s1_reinvestment_compounding")
        
        st.sidebar.markdown("**Separate Monthly SIP Fund (from Scheme 58 Contribution End to Scheme 60 Pension Start)**")
        s1_sip_fund_growth_rate = st.number_input("Scheme 58: Separate SIP Fund Growth Annual Rate (%)", value=8.3, min_value=0.0, max_value=100.0, step=0.1, key="s1_sip_fund_growth_rate") / 100
        s1_sip_fund_compounding_freq_str = st.selectbox("Scheme 58: Separate SIP Fund Compounding", ["Monthly", "Quarterly", "Annually", "Daily"], index=0, key="s1_sip_compounding")
    
    with st.sidebar.expander("Pension Scheme 60 Years Old", expanded=True):
        s2_pension_amount = st.number_input("Scheme 60: Monthly Pension Received (₹)", value=127000.00, min_value=0.0, step=1000.0, key="s2_pension_amount")
        s2_pension_start_date = st.date_input("Scheme 60: Pension Start Date (Assumed to be User's 60th Birthday)", value=date(2028, 6, 1), key="s2_pension_start_date")
        s2_contribution_to_provider_end_date = st.date_input("Scheme 60: Contribution to Provider End Date", value=date(2028, 5, 31), key="s2_contribution_end_date")
        
        st.sidebar.markdown("**Pension Reinvestment Parameters (from Scheme 60 Pension Start)**")
        s2_reinvestment_rate = st.number_input("Scheme 60: Pension Reinvestment Annual Rate (%)", value=7.0, min_value=0.0, max_value=100.0, step=0.1, key="s2_reinvestment_rate") / 100
        s2_reinvestment_compounding_freq_str = st.selectbox("Scheme 60: Pension Reinvestment Compounding", ["Monthly", "Quarterly", "Annually", "Daily"], index=1, key="s2_reinvestment_compounding")
    
    with st.sidebar.expander("Taxation Options", expanded=True):
        enable_tax_implications = st.checkbox("Enable Tax Implications", value=True, key="enable_tax")
        tax_rate_percent = 0.0
        if enable_tax_implications:
            tax_rate_percent = st.number_input("Tax Rate (%) (for income/interest before age 60)", value=30.0, min_value=0.0, max_value=100.0, step=0.1, key="tax_rate")
        tax_rate = tax_rate_percent / 100.0
    
    return {
        'initial_lump_sum': initial_lump_sum,
        'lump_sum_date': lump_sum_date,
        'monthly_contribution': monthly_contribution,
        's1_pension_amount': s1_pension_amount,
        's1_pension_start_date': s1_pension_start_date,
        's1_contribution_to_provider_end_date': s1_contribution_to_provider_end_date,
        's1_reinvestment_rate': s1_reinvestment_rate,
        's1_reinvestment_compounding_freq_str': s1_reinvestment_compounding_freq_str,
        's1_sip_fund_growth_rate': s1_sip_fund_growth_rate,
        's1_sip_fund_compounding_freq_str': s1_sip_fund_compounding_freq_str,
        's2_pension_amount': s2_pension_amount,
        's2_pension_start_date': s2_pension_start_date,
        's2_contribution_to_provider_end_date': s2_contribution_to_provider_end_date,
        's2_reinvestment_rate': s2_reinvestment_rate,
        's2_reinvestment_compounding_freq_str': s2_reinvestment_compounding_freq_str,
        'enable_tax_implications': enable_tax_implications,
        'tax_rate': tax_rate
    }

def create_date_navigation(current_date, min_date, max_possible_date):
    """Create navigation buttons for date selection."""
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
    
    with col1:
        if st.button("◀◀ -1 Year"):
            return current_date - relativedelta(years=1)
    with col2:
        if st.button("◀ -3 Months"):
            return current_date - relativedelta(months=3)
    with col3:
        st.markdown(f"<h3 style='text-align: center;'>{format_date(current_date)}</h3>", unsafe_allow_html=True)
    with col4:
        if st.button("+3 Months ▶"):
            new_date = current_date + relativedelta(months=3)
            return min(new_date, max_possible_date)
    with col5:
        if st.button("+1 Year ▶▶"):
            new_date = current_date + relativedelta(years=1)
            return min(new_date, max_possible_date)
    
    return current_date

def create_scheme_comparison_chart(combined_df):
    """Create a chart comparing both pension schemes over time."""
    if combined_df.empty:
        st.warning("No data available to display chart.")
        return
    
    fig = go.Figure()
    
    # Add traces for each scheme
    fig.add_trace(go.Scatter(
        x=combined_df['Date'], 
        y=combined_df['Scheme 58'],
        mode='lines',
        name='Pension Scheme 58 Years Old',
        line=dict(color='#1f77b4', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=combined_df['Date'], 
        y=combined_df['Scheme 60'],
        mode='lines',
        name='Pension Scheme 60 Years Old',
        line=dict(color='#ff7f0e', width=2)
    ))
    
    # Add markers for overtake points
    overtake_points = []
    prev_diff = 0
    for i in range(1, len(combined_df)):
        curr_diff = combined_df['Scheme 58'].iloc[i] - combined_df['Scheme 60'].iloc[i]
        if (prev_diff <= 0 and curr_diff > 0) or (prev_diff >= 0 and curr_diff < 0):
            overtake_points.append(i)
        prev_diff = curr_diff
    
    for idx in overtake_points:
        date = combined_df['Date'].iloc[idx]
        s58_val = combined_df['Scheme 58'].iloc[idx]
        s60_val = combined_df['Scheme 60'].iloc[idx]
        
        fig.add_trace(go.Scatter(
            x=[date],
            y=[max(s58_val, s60_val)],
            mode='markers',
            marker=dict(size=10, color='red', symbol='star'),
            name=f'Overtake at {date}',
            showlegend=False
        ))
    
    # Update layout
    fig.update_layout(
        title='Pension Scheme Comparison Over Time',
        xaxis_title='Date',
        yaxis_title='Total Accumulated Value (₹)',
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=20, r=20, t=40, b=20),
    )
    
    # Format the y-axis as currency
    fig.update_yaxes(tickprefix='₹', tickformat=',')
    
    st.plotly_chart(fig, use_container_width=True)

def create_summary_cards(s1_final_value, s2_final_value, s1_total_interest, s2_total_interest, 
                        s1_total_pension_tax=0, s2_total_pension_tax=0, 
                        s1_total_reinvestment_tax=0, s2_total_reinvestment_tax=0,
                        enable_tax=False):
    """Create summary cards with key metrics."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="border:1px solid #1f77b4; border-radius:10px; padding:15px; margin:5px;">
            <h3 style="color:#1f77b4; text-align:center;">Pension Scheme 58 Years Old</h3>
            <hr>
            <p style="font-size:18px;"><strong>Total Value:</strong> {}</p>
            <p style="font-size:18px;"><strong>Total Interest Earned:</strong> {}</p>
            {}
        </div>
        """.format(
            format_currency(s1_final_value),
            format_currency(s1_total_interest),
            f'<p style="font-size:18px;"><strong>Total Tax Paid:</strong> {format_currency(s1_total_pension_tax + s1_total_reinvestment_tax)}</p>' if enable_tax else ''
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="border:1px solid #ff7f0e; border-radius:10px; padding:15px; margin:5px;">
            <h3 style="color:#ff7f0e; text-align:center;">Pension Scheme 60 Years Old</h3>
            <hr>
            <p style="font-size:18px;"><strong>Total Value:</strong> {}</p>
            <p style="font-size:18px;"><strong>Total Interest Earned:</strong> {}</p>
            {}
        </div>
        """.format(
            format_currency(s2_final_value),
            format_currency(s2_total_interest),
            f'<p style="font-size:18px;"><strong>Total Tax Paid:</strong> {format_currency(s2_total_pension_tax + s2_total_reinvestment_tax)}</p>' if enable_tax else ''
        ), unsafe_allow_html=True)

def display_scheme_details(df, title, enable_tax_implications):
    """Display detailed scheme information in a tab."""
    st.subheader(title)
    
    # Check if dataframe is empty
    if df.empty:
        st.warning("No data available to display.")
        return
    
    # Create a copy of the dataframe to avoid modifying the original
    display_df = df.copy()
    
    # Format the date column for display without using .dt accessor
    if 'Date' in display_df.columns:
        # Convert to string format if it's not already
        display_df['Date'] = display_df['Date'].astype(str)
        # Try to clean up the date format if possible (remove time part if present)
        display_df['Date'] = display_df['Date'].str.split(' ').str[0]
    
    # Create a simplified dataframe for display
    simplified_df = pd.DataFrame()
    simplified_df['Date'] = display_df['Date']
    
    # Add Pension Received column (net of tax if tax implications enabled)
    if enable_tax_implications and 'Pension Received This Month (Net)' in display_df.columns:
        simplified_df['Pension Received'] = display_df['Pension Received This Month (Net)']
    elif 'Pension Received This Month' in display_df.columns:
        simplified_df['Pension Received'] = display_df['Pension Received This Month']
    elif 'Pension Received This Month (Gross)' in display_df.columns:
        simplified_df['Pension Received'] = display_df['Pension Received This Month (Gross)']
    
    # Add SIP Fund Balance (if applicable)
    if 'Separate SIP Fund Balance' in display_df.columns:
        simplified_df['SIP Fund Balance'] = display_df['Separate SIP Fund Balance']
    
    # Add Pension Reinvestment Pot
    if 'Pension Reinvestment Pot' in display_df.columns:
        simplified_df['Pension Reinvestment Pot'] = display_df['Pension Reinvestment Pot']
    
    # Always add Total Value column
    if 'Total Accumulated Value (User)' in display_df.columns:
        simplified_df['Total Value'] = display_df['Total Accumulated Value (User)']
    
    # Create formatting dictionary for display
    format_dict = {}
    for col in simplified_df.columns:
        if col != 'Date':  # Skip formatting for Date column
            format_dict[col] = "₹{:,.2f}"
    
    # Display the simplified dataframe
    st.dataframe(
        simplified_df.style.format(format_dict),
        height=300,
        use_container_width=True
    )
    
    # Add expandable section for detailed breakdown
    with st.expander("Click to see detailed breakdown"):
        # Create tabs for different types of breakdowns
        breakdown_tabs = st.tabs(["Pension Details", "Investment Details", "Tax Details"])
        
        with breakdown_tabs[0]:
            st.subheader("Pension Breakdown")
            pension_cols = [col for col in display_df.columns if 'Pension' in col and col != 'Pension Reinvestment Pot']
            if pension_cols:
                st.dataframe(
                    display_df[['Date'] + pension_cols].style.format(
                        {col: "₹{:,.2f}" for col in pension_cols}
                    ),
                    height=200,
                    use_container_width=True
                )
            else:
                st.info("No pension details available for this period.")
        
        with breakdown_tabs[1]:
            st.subheader("Investment Breakdown")
            investment_cols = [
                col for col in display_df.columns 
                if any(term in col for term in ['SIP', 'Fund', 'Interest', 'Reinvestment', 'Contributions'])
            ]
            if investment_cols:
                st.dataframe(
                    display_df[['Date'] + investment_cols].style.format(
                        {col: "₹{:,.2f}" for col in investment_cols if col != 'Date'}
                    ),
                    height=200,
                    use_container_width=True
                )
            else:
                st.info("No investment details available for this period.")
        
        with breakdown_tabs[2]:
            st.subheader("Tax Breakdown")
            if enable_tax_implications:
                tax_cols = [col for col in display_df.columns if 'Tax' in col]
                if tax_cols:
                    st.dataframe(
                        display_df[['Date'] + tax_cols].style.format(
                            {col: "₹{:,.2f}" for col in tax_cols}
                        ),
                        height=200,
                        use_container_width=True
                    )
                else:
                    st.info("No tax details available for this period.")
            else:
                st.info("Tax implications are disabled.")

def display_overtakes_and_ranking(overtakes, ranking):
    """Display scheme overtakes and ranking information."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Scheme Overtakes:")
        if overtakes:
            for overtake_info in overtakes:
                st.markdown(f"- {overtake_info}")
        else:
            st.write("No overtakes detected so far for the displayed period.")
    
    with col2:
        st.subheader("Current Ranking:")
        for rank_info in ranking:
            st.markdown(f"- {rank_info}")

def create_scheme_details_tabs(s1_records, s2_records, enable_tax_implications):
    """Create tabs for detailed scheme information."""
    
    # Create tabs for each scheme
    tab1, tab2 = st.tabs(["Scheme 58 Details", "Scheme 60 Details"])
    
    # Ensure we're working with dataframes
    s1_df = s1_records if isinstance(s1_records, pd.DataFrame) else pd.DataFrame(s1_records)
    s2_df = s2_records if isinstance(s2_records, pd.DataFrame) else pd.DataFrame(s2_records)
    
    with tab1:
        display_scheme_details(s1_df, "Pension Scheme 58 Years Old", enable_tax_implications)
    
    with tab2:
        display_scheme_details(s2_df, "Pension Scheme 60 Years Old", enable_tax_implications)