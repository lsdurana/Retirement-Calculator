import streamlit as st
import pandas as pd
import numpy_financial as npf

st.set_page_config(page_title="Retirement Master", layout="wide")

# --- GLOBAL SIDEBAR ---
with st.sidebar:
    st.header("1. Core Assumptions")
    current_age = st.number_input("Current Age", value=35, step=1)
    retire_age = st.slider("Target Retirement Age", 50, 80, 65)
    death_age = st.slider("Planning Horizon (Age)", 80, 110, 95)
    
    st.header("2. Market Rates")
    inflation = st.slider("Inflation Rate (%)", 0.0, 10.0, 3.0) / 100
    returns = st.slider("Annual Return (%)", 0.0, 15.0, 7.0) / 100
    
    st.header("3. Extra Costs")
    medical = st.number_input("Annual Medical Buffer ($)", value=5000)

# --- APP NAVIGATION ---
tab1, tab2, tab3 = st.tabs(["Check Current Path", "Target Goal", "Monthly Savings Plan"])

# Calculate Real Rate of Return
real_rate = (1 + returns) / (1 + inflation) - 1
years_in_retirement = death_age - retire_age
years_to_save = retire_age - current_age

# --- TAB 1: HOW LONG WILL MY MONEY LAST? ---
with tab1:
    st.header("Will my current savings last?")
    assets = st.number_input("Current Retirement Assets ($)", value=500000, step=10000)
    expenses = st.number_input("Annual Living Expenses ($)", value=60000, step=1000)
    
    balance = assets
    data = []
    fail_age = None
    for age in range(retire_age, death_age + 1):
        y = age - retire_age
        current_exp = (expenses + medical) * ((1 + inflation) ** y)
        interest = balance * returns
        balance = (balance + interest) - current_exp
        data.append({"Age": age, "Balance": max(0, balance)})
        if balance <= 0 and fail_age is None: fail_age = age

    st.line_chart(pd.DataFrame(data).set_index("Age"))
    if fail_age:
        st.error(f"⚠️ Funds exhausted at age {fail_age}")
    else:
        st.success(f"✅ Your money lasts until {death_age}+ (Remaining: ${balance:,.2f})")

# --- TAB 2: HOW MUCH DO I NEED? ---
with tab2:
    st.header("Find your 'Target Number'")
    target_expenses = st.number_input("Desired Annual Income in Retirement ($)", value=70000)
    
    if real_rate == 0:
        required_amount = (target_expenses + medical) * years_in_retirement
    else:
        required_amount = (target_expenses + medical
