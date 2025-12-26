import streamlit as st
import pandas as pd

st.set_page_config(page_title="Retirement Forecaster", layout="wide")

st.title("🛡️ Retirement & Longevity Predictor")
st.markdown("Calculate how long your nest egg will last based on inflation and market returns.")

# --- Sidebar Inputs ---
with st.sidebar:
    st.header("Financial Inputs")
    assets = st.number_input("Total Assets ($)", value=1000000, step=10000)
    expenses = st.number_input("Annual Expenses (Today's $)", value=60000, step=1000)
    
    st.header("Timeline")
    retire_age = st.slider("Retirement Age", 50, 80, 65)
    death_age = st.slider("Planning Horizon (Age)", 80, 110, 95)
    
    st.header("Market & Costs")
    inflation = st.slider("Inflation Rate (%)", 0.0, 10.0, 3.0) / 100
    returns = st.slider("Annual Return (%)", 0.0, 15.0, 6.0) / 100
    medical = st.number_input("Annual Medical Buffer ($)", value=5000)

# --- Logic ---
data = []
balance = assets
fail_age = None

for age in range(retire_age, death_age + 1):
    years_passed = age - retire_age
    # Adjusting for inflation
    current_expenses = (expenses + medical) * ((1 + inflation) ** years_passed)
    
    # Growth and Withdrawal
    interest = balance * returns
    balance = (balance + interest) - current_expenses
    
    data.append({
        "Age": age,
        "Balance": max(0, balance),
        "Yearly Withdrawal": current_expenses
    })
    
    if balance <= 0 and fail_age is None:
        fail_age = age

df = pd.DataFrame(data)

# --- Display ---
col1, col2 = st.columns(2)

with col1:
    if fail_age:
        st.error(f"⚠️ Funds exhausted at age {fail_age}")
    else:
        st.success(f"✅ Your money lasts until age {death_age}+")
        st.metric("Final Balance", f"${balance:,.2f}")

with col2:
    st.metric("Total Years Covered", (fail_age - retire_age) if fail_age else (death_age - retire_age))

st.line_chart(df.set_index("Age")["Balance"])
st.subheader("Yearly Breakdown")
st.dataframe(df)
