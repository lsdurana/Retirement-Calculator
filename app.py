import streamlit as st
import pandas as pd
import numpy_financial as npf # You may need to add this to requirements.txt

st.set_page_config(page_title="Retirement Master", layout="wide")

# --- APP NAVIGATION ---
tab1, tab2 = st.tabs(["Check My Current Path", "Calculate My Target Goal"])

# --- COMMON SIDEBAR INPUTS ---
with st.sidebar:
    st.header("Global Assumptions")
    retire_age = st.slider("Target Retirement Age", 50, 80, 65)
    death_age = st.slider("Planning Horizon (Age)", 80, 110, 95)
    inflation = st.slider("Inflation Rate (%)", 0.0, 10.0, 3.0) / 100
    returns = st.slider("Annual Return (%)", 0.0, 15.0, 6.0) / 100
    medical = st.number_input("Annual Medical Buffer ($)", value=5000)

# --- TAB 1: HOW LONG WILL MY MONEY LAST? ---
with tab1:
    st.header("Will my current savings last?")
    assets = st.number_input("Current Retirement Assets ($)", value=1000000, step=10000)
    expenses = st.number_input("Annual Living Expenses ($)", value=60000, step=1000)
    
    # Logic same as before...
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
        st.error(f"Your money runs out at age {fail_age}")
    else:
        st.success(f"You're set! Remaining at {death_age}: ${balance:,.2f}")

# --- TAB 2: HOW MUCH DO I NEED? ---
with tab2:
    st.header("Find your 'Target Number'")
    target_expenses = st.number_input("Desired Annual Income ($)", value=70000)
    
    # Financial Math: Real Rate of Return
    # We use the Fisher Equation to find the 'Inflation-Adjusted Return'
    real_rate = (1 + returns) / (1 + inflation) - 1
    years_in_retirement = death_age - retire_age
    
    # PV of Annuity Formula
    if real_rate == 0:
        required_amount = target_expenses * years_in_retirement
    else:
        required_amount = target_expenses * ((1 - (1 + real_rate) ** -years_in_retirement) / real_rate)

    st.metric(label=f"Your Target Nest Egg at Age {retire_age}", value=f"${required_amount:,.2f}")
    
    st.info(f"""
    **Why this number?** To live on **${target_expenses:,.0f}/year** for **{years_in_retirement} years**, 
    while your money grows at **{returns*100:.1f}%** but prices rise by **{inflation*100:.1f}%**, 
    you need exactly **${required_amount:,.2f}** the day you stop working.
    """)
