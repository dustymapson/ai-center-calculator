import streamlit as st
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, 
    HRFlowable, PageBreak
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfgen import canvas

st.set_page_config(page_title="AI-Center ROI Calculator", page_icon="👁️", layout="wide", initial_sidebar_state="expanded")

# ---------- CSS ----------
st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; color: #ffffff; }

    .big-number { 
        font-size: 2.5rem; 
        font-weight: 700; 
        color: #d4af37; 
        line-height: 1.1; 
        margin: 0.1rem 0; 
    }

    .label { 
        font-size: 0.72rem; 
        color: #ffffff !important; 
        text-transform: uppercase; 
        letter-spacing: 0.06em; 
        margin-bottom: 0.2rem;
    }

    .section-header {
        font-size: 0.75rem;
        font-weight: 700;
        color: #d4af37;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin: 1.1rem 0 0.45rem 0;
        padding-bottom: 0.25rem;
        border-bottom: 1px solid #2a2a2a;
    }

    .sub-label {
        font-size: 0.68rem;
        font-weight: 600;
        color: #888888;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin: 0.35rem 0 0.3rem 0;
    }

    .metric-card {
        background: #141414; 
        border: 1px solid #2a2a2a;
        border-radius: 10px; 
        padding: 0.8rem 0.65rem; 
        text-align: center; 
        height: 100%;
    }

    .metric-card-hero {
        background: #141414; 
        border: 1px solid #d4af37;
        border-radius: 10px; 
        padding: 1rem 0.75rem; 
        text-align: center; 
        height: 100%;
    }

    .metric-value {
        font-size: 1.35rem;
        font-weight: 600;
        color: #ffffff;
        margin-top: 0.1rem;
    }

    .metric-value-gold {
        font-size: 1.35rem;
        font-weight: 600;
        color: #d4af37;
        margin-top: 0.1rem;
    }

    .scenario-bar {
        background: #141414;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
        padding: 0.55rem 1rem;
        margin-bottom: 0.7rem;
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
        align-items: center;
    }

    .pill {
        background: #1f1a0f;
        border: 1px solid #d4af37;
        color: #d4af37;
        font-size: 0.76rem;
        font-weight: 600;
        padding: 0.22rem 0.65rem;
        border-radius: 20px;
        letter-spacing: 0.03em;
    }

    .header-box {
        background: linear-gradient(90deg, #111, #1a1a1a);
        border: 1px solid #333; 
        border-radius: 12px;
        padding: 1rem 1.5rem; 
        margin-bottom: 1rem;
    }

    h1, h2, h3, h4 { color: #ffffff !important; }

    [data-testid="stMetricLabel"] { color: #ffffff !important; }
    [data-testid="stMetricValue"] { color: #ffffff !important; }

    .stCaption, .stMarkdown p { color: #e5e5e5 !important; }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stRadio label {
        color: #111111 !important;
    }

    .stDownloadButton > button {
        background-color: #e5e5e5 !important;
        color: #111111 !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 8px !important;
    }
    .stDownloadButton > button:hover {
        background-color: #d4af37 !important;
        color: #111111 !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown("""
<div class="header-box">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
        <div>
            <h2 style="margin:0; color:#d4af37 !important;">AI-Center ROI Calculator</h2>
            <div style="color:#ffffff; font-size:0.9rem;">Confidential – For Internal Discussion</div>
        </div>
        <div style="color:#cccccc; font-size:0.8rem; text-align:right;">
            Scenario Modeling Tool<br>Not for patient or public use
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------- SIDEBAR ----------
st.sidebar.markdown("### Scenario Presets")

if "last_preset" not in st.session_state:
    st.session_state.last_preset = "Base"

preset = st.sidebar.radio(
    "Select Scenario",
    ["Conservative", "Base", "Aggressive"],
    index=["Conservative", "Base", "Aggressive"].index(st.session_state.last_preset),
    label_visibility="collapsed"
)

if preset != st.session_state.last_preset:
    if preset == "Conservative":
        st.session_state.volume = 200
        st.session_state.capture = 35
        st.session_state.price = 29
    elif preset == "Base":
        st.session_state.volume = 300
        st.session_state.capture = 65
        st.session_state.price = 39
    elif preset == "Aggressive":
        st.session_state.volume = 400
        st.session_state.capture = 75
        st.session_state.price = 49
    st.session_state.last_preset = preset

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
    lease_months = 60

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

# ---------- DISPLAY ----------

# Scenario bar
st.markdown(f"""
<div class="scenario-bar">
    <span class="pill">{purchase_type}</span>
    <span class="pill">{volume} pts/mo</span>
    <span class="pill">{capture}% capture</span>
    <span class="pill">${price}/patient</span>
</div>
""", unsafe_allow_html=True)

# ===== RETURN (now includes Year 1 & Year 2) =====
st.markdown('<div class="section-header">Return</div>', unsafe_allow_html=True)

# Row 1: Hero + Net + Payback
r1, r2, r3 = st.columns([1.4, 1, 1])
with r1:
    st.markdown(f"""
    <div class="metric-card-hero">
        <div class="label">Profit over {term_months}-Month Term</div>
        <div class="big-number">${profit_term:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)
with r2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">Net Profit / Month</div>
        <div class="metric-value-gold">${net:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)
with r3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">Payback Period</div>
        <div class="metric-value">{payback:.1f} mo</div>
    </div>
    """, unsafe_allow_html=True)

# Row 2: Year 1 + Year 2 (now inside Return)
st.markdown("<div style='height:0.35rem'></div>", unsafe_allow_html=True)
y1, y2 = st.columns(2)
with y1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">Profit – Year 1</div>
        <div class="metric-value">${profit_y1:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)
with y2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">Profit – Year 2</div>
        <div class="metric-value">${profit_y2:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

# ===== VOLUME & REVENUE =====
st.markdown('<div class="section-header">Volume & Revenue</div>', unsafe_allow_html=True)

v1, v2 = st.columns(2)
with v1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">Captured Patients / mo</div>
        <div class="metric-value">{captured:.0f}</div>
    </div>
    """, unsafe_allow_html=True)
with v2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">Gross Revenue / mo</div>
        <div class="metric-value">${gross:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

# ===== INVESTMENT & COST (split into Upfront vs Recurring) =====
st.markdown('<div class="section-header">Investment & Cost</div>', unsafe_allow_html=True)

# Upfront subgroup
st.markdown('<div class="sub-label">Upfront</div>', unsafe_allow_html=True)
u1, u2 = st.columns(2)
with u1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">Device Cost</div>
        <div class="metric-value">${device_cost:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)
with u2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">Total Investment</div>
        <div class="metric-value">${total_investment:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

# Recurring subgroup
st.markdown('<div class="sub-label">Recurring (Monthly)</div>', unsafe_allow_html=True)
m1, m2 = st.columns(2)
with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">Monthly Lease Payment</div>
        <div class="metric-value">{"$" + f"{payment:,.2f}" if purchase_type == "Lease" else "—"}</div>
    </div>
    """, unsafe_allow_html=True)
with m2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">Total Monthly Cost</div>
        <div class="metric-value">${monthly_cost:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

with st.expander("Assumptions & Notes"):
    st.markdown("""
**Capture Rate Guidance**  
- 35% = Very Conservative | 65% = Typical / Base | 75%+ = Strong trust + optimized workflow  

**Net Profit** = Gross revenue − Lease payment − BioAge − Maintenance − Other monthly costs.  

**Setup / Install / Tax** is a residual placeholder (originally $28,175 − $22,000 device = $6,175).  
Edit it for each deal.
    """)

# ==================== PDF ====================
def draw_bg(canvas_obj, doc):
    page_w, page_h = letter
    canvas_obj.setFillColor(colors.HexColor("#0a0a0a"))
    canvas_obj.rect(0, 0, page_w, page_h, fill=1, stroke=0)
    canvas_obj.setStrokeColor(colors.HexColor("#d4af37"))
    canvas_obj.setLineWidth(1.5)
    canvas_obj.line(40, page_h - 30, page_w - 40, page_h - 30)
    canvas_obj.line(40, 36, page_w - 40, 36)

def create_combined_pdf():
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        rightMargin=0.5*inch, leftMargin=0.5*inch,
        topMargin=0.55*inch, bottomMargin=0.48*inch
    )

    GOLD = colors.HexColor("#d4af37")
    GOLD_DIM = colors.HexColor("#b8962e")
    WHITE = colors.HexColor("#ffffff")
    DARK = colors.HexColor("#141414")
    BLACK = colors.HexColor("#0a0a0a")

    title_style = ParagraphStyle('Title', fontName='Helvetica-Bold', fontSize=17, textColor=GOLD, spaceAfter=6, leading=20)
    subtitle_style = ParagraphStyle('Sub', fontName='Helvetica-Bold', fontSize=8, textColor=WHITE, spaceAfter=10, spaceBefore=1)
    section_style = ParagraphStyle('Sec', fontName='Helvetica-Bold', fontSize=10, textColor=GOLD, spaceBefore=9, spaceAfter=5)
    label_style = ParagraphStyle('Lab', fontName='Helvetica-Bold', fontSize=9, textColor=WHITE, alignment=TA_CENTER, spaceAfter=4)
    big_style = ParagraphStyle('Big', fontName='Helvetica-Bold', fontSize=24, textColor=GOLD, alignment=TA_CENTER, spaceBefore=6, spaceAfter=6, leading=28)
    sub_label_style = ParagraphStyle('SubLab', fontName='Helvetica-Bold', fontSize=8, textColor=WHITE, alignment=TA_CENTER, spaceBefore=2, spaceAfter=9)
    footer_style = ParagraphStyle('Foot', fontName='Helvetica-Bold', fontSize=7, textColor=WHITE, alignment=TA_CENTER, leading=9)

    story = []

    # PAGE 1 - SUMMARY
    story.append(Paragraph("AI-CENTER  //  ROI SUMMARY", title_style))
    story.append(Paragraph(f"GENERATED {datetime.now().strftime('%Y.%m.%d  %H:%M').upper()}  ·  CONFIDENTIAL", subtitle_style))
    
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"PROFIT OVER {term_months}-MONTH TERM", label_style))
    story.append(Paragraph(f"${profit_term:,.0f}", big_style))
    story.append(Paragraph(f"{purchase_type.upper()}  ·  {capture}% CAPTURE  ·  ${price}/PATIENT", sub_label_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=GOLD, spaceBefore=2, spaceAfter=10))

    data = [
        ["NET PROFIT / MO", f"${net:,.0f}", "PAYBACK", f"{payback:.1f} MO"],
        ["PROFIT YEAR 1", f"${profit_y1:,.0f}", "PROFIT YEAR 2", f"${profit_y2:,.0f}"],
        ["CAPTURED / MO", f"{captured:.0f}", "GROSS REVENUE / MO", f"${gross:,.0f}"],
    ]
    t = Table(data, colWidths=[1.7*inch, 1.5*inch, 1.7*inch, 1.5*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), DARK),
        ('TEXTCOLOR', (0, 0), (-1, -1), WHITE),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
        ('TEXTCOLOR', (1, 0), (1, -1), GOLD),
        ('TEXTCOLOR', (3, 0), (3, -1), GOLD),
        ('GRID', (0, 0), (-1, -1), 0.7, GOLD),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
    ]))
    story.append(t)
    story.append(Spacer(1, 12))

    # Monthly Cost Breakdown
    story.append(Paragraph("MONTHLY COST BREAKDOWN", section_style))

    nw500_label = "NW500 Lease / Finance" if purchase_type == "Lease" and payment > 0 else "NW500 Finance"
    nw500_value = f"${payment:,.2f}" if payment > 0 else "$0.00 (Cash / No Device)"

    cost_data = [
        [nw500_label, nw500_value],
        ["BioAge Subscription", f"${bioage:,.2f}"],
        ["Maintenance", f"${maint:,.2f}"],
        ["Other (staff / consumables)", f"${other_monthly:,.2f}"],
        ["TOTAL MONTHLY COST", f"${monthly_cost:,.2f}"],
    ]
    t_cost = Table(cost_data, colWidths=[3.6*inch, 2.8*inch])
    t_cost.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -2), DARK),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#1f1a0f")),
        ('TEXTCOLOR', (0, 0), (-1, -1), WHITE),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('TEXTCOLOR', (1, 0), (1, -2), GOLD),
        ('TEXTCOLOR', (1, -1), (1, -1), GOLD),
        ('GRID', (0, 0), (-1, -1), 0.6, GOLD),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_cost)
    story.append(Spacer(1, 12))

    # Scenario Inputs
    story.append(Paragraph("SCENARIO INPUTS", section_style))
    inp = [
        ["DEVICE COST", f"${device_cost:,.0f}", "SETUP / TAX", f"${setup_cost:,.0f}"],
        ["TOTAL INVESTMENT", f"${total_investment:,.0f}", "PURCHASE TYPE", purchase_type.upper()],
        ["INTEREST RATE", f"{interest_rate}%", "TERM", f"{term_months} MONTHS"],
        ["PATIENT VOLUME", f"{volume}", "CAPTURE RATE", f"{capture}%"],
        ["PRICE / PATIENT", f"${price}", "", ""],
    ]
    t2 = Table(inp, colWidths=[1.7*inch, 1.5*inch, 1.7*inch, 1.5*inch])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), DARK),
        ('TEXTCOLOR', (0, 0), (-1, -1), WHITE),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, GOLD_DIM),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t2)
    story.append(Spacer(1, 14))
    story.append(Paragraph(
        "DISCLAIMER: These figures are estimates only and do not constitute financial, legal, or clinical advice. "
        "Actual results will vary.  ·  CONFIDENTIAL – FOR INTERNAL DISCUSSION ONLY  ·  AI-CENTER",
        footer_style
    ))

    # PAGE 2 - PRO FORMA MATRIX
    story.append(PageBreak())
    story.append(Paragraph("AI-CENTER  //  PRO FORMA MATRIX", title_style))
    story.append(Paragraph(
        f"DEVICE ${device_cost:,.0f} + SETUP ${setup_cost:,.0f}  ·  {interest_rate}%  ·  {term_months} MO  ·  BIOAGE ${bioage} + MAINT ${maint}",
        subtitle_style
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=GOLD, spaceAfter=8))

    def calc_row(vol, cap, pr):
        capt = vol * (cap / 100)
        gr = capt * pr
        nt = gr - monthly_cost
        if nt > 0:
            pb = total_investment / nt
            y1 = nt * max(0, 12 - pb) if pb < 12 else 0
            y2 = nt * 12
            over = (nt * term_months) - total_investment
        else:
            pb, y1, y2, over = 999, 0, 0, -total_investment
        return [
            str(vol), f"{capt:.0f}", f"${gr:,.0f}", f"${nt:,.0f}",
            f"{pb:.1f}", f"${y1:,.0f}" if y1 > 0 else "—", f"${y2:,.0f}", f"${over:,.0f}"
        ]

    headers = ["Pts/mo", "Captured", "Gross", "Net/mo", "Payback", "Profit Y1", "Profit Y2", "Over Term"]

    for price_point, label in [(49, "$49 / PATIENT"), (39, "$39 / PATIENT"), (29, "$29 / PATIENT")]:
        story.append(Paragraph(label, section_style))
        rows = [headers]
        for cap_rate, cap_name in [(35, "Very Conservative (35%)"), (65, "Standard (65%)"), (75, "Best Case (75%)")]:
            rows.append([cap_name, "", "", "", "", "", "", ""])
            for vol in [200, 300, 400]:
                rows.append(calc_row(vol, cap_rate, price_point))

        col_w = [0.7*inch, 0.75*inch, 0.85*inch, 0.85*inch, 0.75*inch, 0.9*inch, 0.9*inch, 1.0*inch]
        t = Table(rows, colWidths=col_w)

        style_cmds = [
            ('BACKGROUND', (0, 0), (-1, 0), GOLD),
            ('TEXTCOLOR', (0, 0), (-1, 0), BLACK),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.4, GOLD_DIM),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('BACKGROUND', (0, 1), (-1, -1), DARK),
            ('TEXTCOLOR', (0, 1), (-1, -1), WHITE),
        ]

        for i, row in enumerate(rows):
            if "Conservative" in str(row[0]) or "Standard" in str(row[0]) or "Best Case" in str(row[0]):
                style_cmds.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor("#1f1a0f")))
                style_cmds.append(('TEXTCOLOR', (0, i), (-1, i), GOLD))
                style_cmds.append(('SPAN', (0, i), (-1, i)))

        t.setStyle(TableStyle(style_cmds))
        story.append(t)
        story.append(Spacer(1, 6))

    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "DISCLAIMER: These figures are estimates only and do not constitute financial, legal, or clinical advice. "
        "Actual results will vary.  ·  CONFIDENTIAL – FOR INTERNAL DISCUSSION ONLY  ·  AI-CENTER",
        footer_style
    ))

    doc.build(story, onFirstPage=draw_bg, onLaterPages=draw_bg)
    buffer.seek(0)
    return buffer

# ---------- DOWNLOAD ----------
pdf_buffer = create_combined_pdf()
st.download_button(
    label="Print Summary + Pro Forma (PDF)",
    data=pdf_buffer,
    file_name=f"AI_Center_ROI_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
    mime="application/pdf",
    use_container_width=True
)

st.markdown("---")
st.caption("""
**Disclaimer:** These figures are estimates only and do not constitute financial, legal, or clinical advice. 
Actual results will vary based on practice volume, patient mix, capture rates, pricing, and operational factors.
""")
