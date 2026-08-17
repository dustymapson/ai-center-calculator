import streamlit as st
import math

st.set_page_config(
    page_title="AI-Center ROI Calculator",
    page_icon="👁️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ---------- Custom CSS ----------
st.markdown("""
<style>
    .stApp { background-color: #0b1220; color: #e2e8f0; }
    .big-number { font-size: 2.6rem; font-weight: 700; color: #22d3ee; line-height: 1.1; }
    .label { font-size: 0.85rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; }
    .metric-card {
        background: #111827; border: 1px solid #1e293b;
        border-radius: 12px; padding: 1.1rem; text-align: center;
    }
    h1, h2, h3, h4 { color: #f1f5f9 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("### AI-Center ROI Calculator")
st.markdown("##### Fully Customizable  ·  Lease or Cash Scenarios")
st.markdown("---")

# ===================== INPUTS =====================
st.sidebar.header("Revenue Assumptions")
volume = st.sidebar.slider("Monthly Patient Volume", 50, 600, 300, 10)
capture = st.sidebar.slider("Capture Rate (%)", 10, 95, 65, 5)
price = st.sidebar.slider("Price per Patient ($)", 15, 70, 39, 1)

st.sidebar.header("Device & Finance")
device_cost = st.sidebar.number_input("Device Cost ($)", min_value=0, value=22000, step=500)
setup_cost = st.sidebar.number_input("Setup / Install / Tax ($)", min_value=0, value=6175, step=100)
interest_rate = st.sidebar.slider("Annual Interest Rate (%)", 0.0, 15.0, 8.0, 0.25)
lease_months = st.sidebar.slider("Lease Term (months)", 12, 84, 60, 6)

st.sidebar.header("Recurring Costs")
bioage = st.sidebar.number_input("BioAge Subscription ($/mo)", min_value=0, value=399, step=10)
maint = st.sidebar.number_input("Maintenance ($/mo)", min_value=0, value=20, step=5)

# ===================== CALCULATIONS =====================
total_investment = device_cost + setup_cost

# Monthly lease payment (standard amortization)
if interest_rate > 0 and lease_months > 0:
    r = (interest_rate / 100) / 12          # monthly rate
    payment = total_investment * (r * (1 + r)**lease_months) / ((1 + r)**lease_months - 1)
else:
    payment = total_investment / lease_months if lease_months > 0 else 0

monthly_cost = payment + bioage + maint

captured = volume * (capture / 100)
gross = captured * price
net = gross - monthly_cost

if net > 0:
    payback = total_investment / net
    profit_y1 = net * max(0, 12 - payback) if payback < 12 else 0
    profit_y2 = net * 12
    profit_lease = (net * lease_months) - total_investment
else:
    payback = 999
    profit_y1 = 0
    profit_y2 = 0
    profit_lease = -total_investment

# ===================== DISPLAY =====================
st.markdown(f"""
<div style="text-align:center">
    <div class="label">Profit over {lease_months}-Month Term</div>
    <div class="big-number">${profit_lease:,.0f}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Key metrics
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f'<div class="metric-card"><div class="label">Captured / mo</div><div style="font-size:1.5rem;font-weight:600">{captured:.0f}</div></div>', unsafe_allow_html=True)
with m2:
    st.markdown(f'<div class="metric-card"><div class="label">Net Profit / mo</div><div style="font-size:1.5rem;font-weight:600;color:#22d3ee">${net:,.0f}</div></div>', unsafe_allow_html=True)
with m3:
    st.markdown(f'<div class="metric-card"><div class="label">Payback</div><div style="font-size:1.5rem;font-weight:600">{payback:.1f} mo</div></div>', unsafe_allow_html=True)
with m4:
    st.markdown(f'<div class="metric-card"><div class="label">Year 2 Profit</div><div style="font-size:1.5rem;font-weight:600">${profit_y2:,.0f}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Secondary metrics
c1, c2, c3 = st.columns(3)
c1.metric("Monthly Lease Payment", f"${payment:,.2f}")
c2.metric("Total Monthly Cost", f"${monthly_cost:,.2f}")
c3.metric("Total Investment", f"${total_investment:,.0f}")

c4, c5 = st.columns(2)
c4.metric("Profit Year 1", f"${profit_y1:,.0f}")
c5.metric("Gross Revenue / mo", f"${gross:,.0f}")

st.markdown("---")
st.caption(f"Device ${device_cost:,.0f} + Setup ${setup_cost:,.0f}  ·  {interest_rate}% interest  ·  {lease_months} months  ·  BioAge ${bioage} + Maint ${maint}")
