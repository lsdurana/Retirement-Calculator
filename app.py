import streamlit as st
import pandas as pd
import numpy_financial as npf

st.set_page_config(page_title="Retirement Master 2025", layout="wide")

# --- SIDEBAR ---
with st.sidebar:
    st.header("1. Personal Timeline")
    current_age = st.number_input("Current Age", min_value=18, max_value=100, value=35)
    retire_age = st.slider("Retirement Age", 50, 85, 65)
    death_age = st.slider("Life Expectancy", 80, 110, 95)
    
    st.header("2. Financial Assumptions")
    # Using decimals for calculations but sliders for user-friendliness
    returns_pct = st.slider("Annual Return (%)", 0.0, 15.0, 7.0)
    inflation_pct = st.slider("Inflation Rate (%)", 0.0, 10.0, 3.0)
    
    returns = returns_pct / 100
    inflation = inflation_pct / 100
    
    # Calculate Real Rate of Return (Fisher Equation)
    if returns == inflation:
        real_rate = 0.0001 # Prevent division by zero
    else:
        real_rate = (1 + returns) / (1 + inflation) - 1

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["📊 Current Forecast", "🎯 Target Goal", "💰 Monthly Savings Plan"])

# --- SHARED CALCULATIONS ---
years_in_retirement = max(1, death_age - retire_age)
years_to_save = max(1, retire_age - current_age)

# --- TAB 1: CURRENT FORECAST ---
with tab1:
    st.header("Will your current nest egg last?")
    current_assets = st.number_input("Current Savings ($)", value=250000, step=10000)
    annual_spend = st.number_input("Annual Expenses (Today's $)", value=50000, step=1000)
    medical_buffer = st.number_input("Annual Medical Buffer ($)", value=5000)
    
    total_annual_out = annual_spend + medical_buffer
    
    balance = current_assets
    history = []
    fail_age = None
    
    for age in range(retire_age, death_age + 1):
        y = age - retire_age
        # Adjust withdrawal for inflation
        inflated_withdrawal = total_annual_out * ((1 + inflation) ** y)
        
        # Apply growth then withdraw
        interest = balance * returns
        balance = (balance + interest) - inflated_withdrawal
        
        history.append({"Age": age, "Balance": max(0, balance)})
        if balance <= 0 and fail_age is None:
            fail_age = age

    df = pd.DataFrame(history)
    st.line_chart(df.set_index("Age"))
    
    if fail_age:
        st.error(f"⚠️ Your funds are projected to run out at age {fail_age}.")
    else:
        st.success(f"✅ Your money lasts until age {death_age}. Final Balance: ${balance:,.2f}")

# --- TAB 2: TARGET GOAL ---
with tab2:
    st.header("What is your 'Magic Number'?")
    st.write(f"To spend **${total_annual_out:,.0f}**/year (adjusted for inflation) for **{years_in_retirement}** years:")
    
    # Present Value of an Annuity formula
    if real_rate <= 0:
        target_nest_egg = total_annual_out * years_in_retirement
    else:
        target_nest_egg = total_annual_out * ((1 - (1 + real_rate) ** -years_in_retirement) / real_rate)
    
    st.metric("Required at Retirement", f"${target_nest_egg:,.2f}")
    st.info("This is the amount you need in your account the day you retire to safely reach your life expectancy.")

# --- TAB 3: SAVINGS PLAN ---
with tab3:
    st.header("How to get there")
    
    # Step 1: Growth of existing money
    future_value_of_current = current_assets * ((1 + returns) ** years_to_save)
    gap = target_nest_egg - future_value_of_current
    
    if gap <= 0:
        st.balloons()
        st.success("Your current assets are already on track to hit your goal! Just keep them invested.")
    else:
        # Step 2: Monthly payment needed to fill the gap
        monthly_rate = returns / 12
        months = years_to_save * 12
        
        # pmt(rate, nper, pv, fv)
        monthly_req = npf.pmt(monthly_rate, months, 0, -gap)
        
        st.metric("Required Monthly Savings", f"${monthly_req:,.2f}")
        st.write(f"Save this amount every month for the next **{years_to_save}** years to reach your **${target_nest_egg:,.2f}**
