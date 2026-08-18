import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="AI-Center ROI Calculator",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- CSS ----------
st.markdown("""
<style>
    .stApp { background-color: #0b1220; color: #e2e8f0; }
    .big-number { font-size: 2.8rem; font-weight: 700; color: #22d3ee; line-height: 1.1; margin: 0.2rem 0; }
    .label { font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.06em; }
    .metric-card {
        background: #111827; border: 1px solid #1e293b;
        border-radius: 12px; padding: 1.1rem 0.8rem; text-align: center;
        height: 100%;
    }
    .header-box {
        background: linear-gradient(90deg, #0f172a, #1e293b);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin-bottom: 1rem;
    }
    h1, h2, h3, h4 { color: #f1f5f9 !important; }
    .stButton > button {
        background-color: #1e293b;
        color: #e2e8f0;
        border: 1px solid #334155;
        border-radius: 8px;
    }
    .stButton > button:hover {
        border-color: #22d3ee;
        color: #22d3ee;
    }
    div[data-testid="stExpander"] {
        background-color: #111827;
        border: 1px solid #1e293b;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown("""
<div class="header-box">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
        <div>
            <h2 style="margin:0; color:#22d3ee !important;">AI-Center ROI Calculator</h2>
            <div style="color:#94a3b8; font-size:0.9rem;">Topcon Healthcare  ·  Confidential – For Internal Discussion</div>
        </div>
        <div style="color:#64748b; font-size:0.8rem; text-align:right;">
            Scenario Modeling Tool<br>Not for patient or public use
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------- SIDEBAR INPUTS ----------
st.sidebar.markdown("### Scenario Presets")
col_p1, col_p2, col_p3 = st.sidebar.columns(3)
if col_p1.button("Conservative", use_container_width=True):
    st.session_state.volume = 200
    st.session_state.capture = 35
    st.session_state.price = 29
if col_p2.button("Base", use_container_width=True):
    st.session_state.volume = 300
    st.session_state.capture = 65
    st.session_state.price = 39
if col_p3.button("Aggressive", use_container_width=True):
    st.session_state.volume = 400
    st.session_state.capture = 75
    st.session_state.price = 49

# Initialize session state defaults
defaults = {
    "volume": 300, "capture": 65, "price": 39,
    "device_cost": 22000, "setup_cost": 6175,
    "interest_rate": 8.0, "lease_months": 60,
    "bioage": 399, "maint": 20, "other_monthly": 0
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

st.sidebar.markdown("---")
st.sidebar.markdown("### Revenue")
volume = st.sidebar.slider("Monthly Patient Volume", 50, 600, st.session_state.volume, 10, key="volume")
capture = st.sidebar.slider("Capture Rate (%)", 10, 95, st.session_state.capture, 5, key="capture")
price = st.sidebar.slider("Price per Patient ($)", 15, 70, st.session_state.price, 1, key="price")

st.sidebar.markdown("### Device & Finance")
purchase_type = st.sidebar.radio("Purchase Type", ["Lease", "Cash Purchase"], horizontal=True)
device_cost = st.sidebar.number_input("Device Cost ($)", min_value=0, value=st.session_state.device_cost, step=500, key="device_cost")
setup_cost = st.sidebar.number_input("Setup / Install / Tax ($)", min_value=0, value=st.session_state.setup_cost, step=100, key="setup_cost")

if purchase_type == "Lease":
    interest_rate = st.sidebar.slider("Annual Interest Rate (%)", 0.0, 15.0, st.session_state.interest_rate, 0.25, key="interest_rate")
    lease_months = st.sidebar.slider("Lease Term (months)", 12, 84, st.session_state.lease_months, 6, key="lease_months")
else:
    interest_rate = 0.0
    lease_months = 60  # used only for "profit over term" comparison

st.sidebar.markdown("### Recurring Monthly Costs")
bioage = st.sidebar.number_input("BioAge Subscription ($)", min_value=0, value=st.session_state.bioage, step=10, key="bioage")
maint = st.sidebar.number_input("Maintenance ($)", min_value=0, value=st.session_state.maint, step=5, key="maint")
other_monthly = st.sidebar.number_input("Other (staff / consumables) ($)", min_value=0, value=st.session_state.other_monthly, step=10, key="other_monthly")

# ---------- CALCULATIONS ----------
total_investment = device_cost + setup_cost

if purchase_type == "Lease" and interest_rate > 0 and lease_months > 0:
    r = (interest_rate / 100) / 12
    payment = total_investment * (r * (1 + r)**lease_months) / ((1 + r)**lease_months - 1)
else:
    # Cash purchase → no monthly lease payment (or spread for comparison)
    payment = 0 if purchase_type == "Cash Purchase" else (total_investment / lease_months if lease_months else 0)

monthly_cost = payment + bioage + maint + other_monthly
captured = volume * (capture / 100)
gross = captured * price
net = gross - monthly_cost

term_months = lease_months if purchase_type == "Lease" else 60

if net > 0:
    payback = total_investment / net
    profit_y1 = net * max(0, 12 - payback) if payback < 12 else 0
    profit_y2 = net * 12
    profit_term = (net * term_months) - total_investment
else:
    payback = 999
    profit_y1 = 0
    profit_y2 = 0
    profit_term = -total_investment

# ---------- MAIN DISPLAY ----------
left, right = st.columns([1.1, 1])

with left:
    st.markdown(f"""
    <div style="text-align:center; padding: 1rem 0;">
        <div class="label">Estimated Profit over {term_months}-Month Term</div>
        <div class="big-number">${profit_term:,.0f}</div>
        <div style="color:#64748b; font-size:0.85rem; margin-top:0.3rem;">
            {purchase_type}  ·  {capture}% capture  ·  ${price}/patient
        </div>
    </div>
    """, unsafe_allow_html=True)

with right:
    m1, m2 = st.columns(2)
    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="label">Net Profit / Month</div>
            <div style="font-size:1.7rem; font-weight:600; color:#22d3ee;">${net:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="label">Payback Period</div>
            <div style="font-size:1.7rem; font-weight:600;">{payback:.1f} mo</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Secondary metrics
c1, c2, c3, c4 = st.columns(4)
c1.metric("Captured Patients / mo", f"{captured:.0f}")
c2.metric("Gross Revenue / mo", f"${gross:,.0f}")
c3.metric("Monthly Lease Payment", f"${payment:,.2f}" if purchase_type == "Lease" else "—")
c4.metric("Total Monthly Cost", f"${monthly_cost:,.2f}")

c5, c6, c7 = st.columns(3)
c5.metric("Profit – Year 1", f"${profit_y1:,.0f}")
c6.metric("Profit – Year 2", f"${profit_y2:,.0f}")
c7.metric("Total Investment", f"${total_investment:,.0f}")

# ---------- ASSUMPTIONS ----------
with st.expander("Assumptions & Notes (click to expand)"):
    st.markdown("""
**Capture Rate Guidance**
- 35% = Very Conservative (reluctant or lower-volume practices)
- 65% = Typical / Base case with good communication
- 75%+ = Strong trust + optimized workflow

**Price per Patient**
- Reflects the incremental fee charged for the AI-Center / BioAge analysis
- Common range observed: $29 – $49

**What is included in Net Profit**
- Gross revenue from captured patients minus:
  - Lease payment (or $0 if cash)
  - BioAge subscription
  - Maintenance
  - Any “Other” monthly costs you enter (staff time, consumables, etc.)

**What is NOT included**
- Staff training time (one-time)
- Marketing spend
- Opportunity cost of chair time
- Potential downstream referral revenue

**Lease vs Cash**
- Lease: monthly payment calculated with standard amortization
- Cash: no monthly finance cost; full investment recovered through net profit
    """)

# ---------- DOWNLOAD SUMMARY ----------
summary = f"""
AI-CENTER ROI SUMMARY
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}
========================================
SCENARIO
  Purchase Type:     {purchase_type}
  Monthly Volume:    {volume}
  Capture Rate:      {capture}%
  Price per Patient: ${price}

DEVICE & FINANCE
  Device Cost:       ${device_cost:,.0f}
  Setup/Install/Tax: ${setup_cost:,.0f}
  Total Investment:  ${total_investment:,.0f}
  Interest Rate:     {interest_rate}%
  Term:              {term_months} months

MONTHLY ECONOMICS
  Captured Patients: {captured:.0f}
  Gross Revenue:     ${gross:,.0f}
  Lease Payment:     ${payment:,.2f}
  BioAge + Maint:    ${bioage + maint:,.0f}
  Other Costs:       ${other_monthly:,.0f}
  Total Monthly Cost:${monthly_cost:,.2f}
  Net Profit / mo:   ${net:,.0f}

RETURNS
  Payback Period:    {payback:.1f} months
  Profit Year 1:     ${profit_y1:,.0f}
  Profit Year 2:     ${profit_y2:,.0f}
  Profit over Term:  ${profit_term:,.0f}

----------------------------------------
Confidential – For internal discussion only
Topcon Healthcare | AI-Center
"""

st.download_button(
    label="Download Text Summary",
    data=summary,
    file_name=f"AI_Center_ROI_Summary_{datetime.now().strftime('%Y%m%d')}.txt",
    mime="text/plain"
)

st.markdown("---")
st.caption("AI-Center ROI Calculator  ·  Topcon Healthcare  ·  For internal use only  ·  Results are estimates and do not constitute financial advice")
