import streamlit as st

st.set_page_config(
    page_title="AI-Center ROI Calculator",
    page_icon="👁️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------- Custom CSS (dark medical theme) ----------
st.markdown("""
<style>
    .stApp {
        background-color: #0b1220;
        color: #e2e8f0;
    }
    .big-number {
        font-size: 2.8rem;
        font-weight: 700;
        color: #22d3ee;
        line-height: 1.1;
    }
    .label {
        font-size: 0.9rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-card {
        background: #111827;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
    }
    h1, h2, h3 {
        color: #f1f5f9 !important;
    }
    .stSlider > div > div > div {
        background-color: #22d3ee;
    }
</style>
""", unsafe_allow_html=True)

# ---------- Header ----------
st.markdown("### AI-Center ROI Calculator")
st.markdown("##### Simplified Pro Forma  ·  60-Month Lease")
st.markdown("---")

# ---------- Inputs ----------
col1, col2, col3 = st.columns(3)

with col1:
    volume = st.slider("Monthly Patient Volume", 100, 500, 300, 10)

with col2:
    capture = st.slider("Capture Rate (%)", 20, 90, 65, 5)

with col3:
    price = st.slider("Price per Patient ($)", 25, 55, 39, 1)

# ---------- Constants (from your pro forma) ----------
MONTHLY_COST = 817.39
INVESTMENT = 28175.31
LEASE_MONTHS = 60

# ---------- Calculations ----------
captured = volume * (capture / 100)
gross = captured * price
net = gross - MONTHLY_COST

if net > 0:
    payback = INVESTMENT / net
    profit_y1 = net * max(0, 12 - payback) if payback < 12 else 0
    profit_y2 = net * 12
    profit_lease = (net * LEASE_MONTHS) - INVESTMENT
else:
    payback = 999
    profit_y1 = 0
    profit_y2 = 0
    profit_lease = -INVESTMENT

# ---------- Big Headline ----------
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(f"""
<div style="text-align:center">
    <div class="label">Profit over 60-Month Lease</div>
    <div class="big-number">${profit_lease:,.0f}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------- Key Metrics ----------
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">Captured / mo</div>
        <div style="font-size:1.6rem;font-weight:600;color:#f1f5f9">{captured:.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">Net Profit / mo</div>
        <div style="font-size:1.6rem;font-weight:600;color:#22d3ee">${net:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">Payback</div>
        <div style="font-size:1.6rem;font-weight:600;color:#f1f5f9">{payback:.1f} mo</div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">Year 2 Profit</div>
        <div style="font-size:1.6rem;font-weight:600;color:#f1f5f9">${profit_y2:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------- Secondary row ----------
s1, s2 = st.columns(2)
with s1:
    st.metric("Profit Year 1", f"${profit_y1:,.0f}")
with s2:
    st.metric("Gross Revenue / mo", f"${gross:,.0f}")

st.markdown("---")
st.caption("Assumptions: Monthly cost $817.39  ·  Year 1 Investment $28,175.31  ·  60-month lease  ·  Simplified model of the AI-Center Pro Forma")
