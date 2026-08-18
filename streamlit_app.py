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
    .stApp { background-color: #0a0a0a; color: #f5f5f5; }
    .big-number { font-size: 2.8rem; font-weight: 700; color: #d4af37; line-height: 1.1; margin: 0.2rem 0; }
    .label { font-size: 0.8rem; color: #a3a3a3; text-transform: uppercase; letter-spacing: 0.06em; }
    .metric-card {
        background: #141414; border: 1px solid #2a2a2a;
        border-radius: 12px; padding: 1.1rem 0.8rem; text-align: center; height: 100%;
    }
    .header-box {
        background: linear-gradient(90deg, #111, #1a1a1a);
        border: 1px solid #333; border-radius: 12px;
        padding: 1rem 1.5rem; margin-bottom: 1rem;
    }
    h1, h2, h3, h4 { color: #f5f5f5 !important; }

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
            <div style="color:#a3a3a3; font-size:0.9rem;">Confidential – For Internal Discussion</div>
        </div>
        <div style="color:#737373; font-size:0.8rem; text-align:right;">
            Scenario Modeling Tool<br>Not for patient or public use
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------- SIDEBAR ----------
st.sidebar.markdown("### Scenario Presets")
c1, c2, c3 = st.sidebar.columns(3)
if c1.button("Conservative", use_container_width=True):
    st.session_state.volume, st.session_state.capture, st.session_state.price = 200, 35, 29
if c2.button("Base", use_container_width=True):
    st.session_state.volume, st.session_state.capture, st.session_state.price = 300, 65, 39
if c3.button("Aggressive", use_container_width=True):
    st.session_state.volume, st.session_state.capture, st.session_state.price = 400, 75, 49

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
left, right = st.columns([1.1, 1])
with left:
    st.markdown(f"""
    <div style="text-align:center; padding: 1rem 0;">
        <div class="label">Estimated Profit over {term_months}-Month Term</div>
        <div class="big-number">${profit_term:,.0f}</div>
        <div style="color:#a3a3a3; font-size:0.85rem; margin-top:0.3rem;">
            {purchase_type} · {capture}% capture · ${price}/patient
        </div>
    </div>
    """, unsafe_allow_html=True)

with right:
    m1, m2 = st.columns(2)
    with m1:
        st.markdown(f'<div class="metric-card"><div class="label">Net Profit / Month</div><div style="font-size:1.7rem;font-weight:600;color:#d4af37">${net:,.0f}</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card"><div class="label">Payback Period</div><div style="font-size:1.7rem;font-weight:600">{payback:.1f} mo</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Captured Patients / mo", f"{captured:.0f}")
c2.metric("Gross Revenue / mo", f"${gross:,.0f}")
c3.metric("Monthly Lease Payment", f"${payment:,.2f}" if purchase_type == "Lease" else "—")
c4.metric("Total Monthly Cost", f"${monthly_cost:,.2f}")

c5, c6, c7 = st.columns(3)
c5.metric("Profit – Year 1", f"${profit_y1:,.0f}")
c6.metric("Profit – Year 2", f"${profit_y2:,.0f}")
c7.metric("Total Investment", f"${total_investment:,.0f}")

with st.expander("Assumptions & Notes"):
    st.markdown("""
**Capture Rate Guidance**  
- 35% = Very Conservative | 65% = Typical / Base | 75%+ = Strong trust + optimized workflow  

**Net Profit** = Gross revenue − Lease payment − BioAge − Maintenance − Other monthly costs.  
**Not included**: training, marketing, chair-time opportunity cost, downstream referral revenue.
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
        topMargin=0.6*inch, bottomMargin=0.5*inch
    )

    GOLD = colors.HexColor("#d4af37")
    GOLD_DIM = colors.HexColor("#b8962e")
    WHITE = colors.HexColor("#ffffff")
    DARK = colors.HexColor("#141414")
    BLACK = colors.HexColor("#0a0a0a")

    title_style = ParagraphStyle('Title', fontName='Helvetica-Bold', fontSize=18, textColor=GOLD, spaceAfter=8, leading=22)
    subtitle_style = ParagraphStyle('Sub', fontName='Helvetica-Bold', fontSize=8, textColor=WHITE, spaceAfter=14, spaceBefore=2)
    section_style = ParagraphStyle('Sec', fontName='Helvetica-Bold', fontSize=10, textColor=GOLD, spaceBefore=10, spaceAfter=6)
    label_style = ParagraphStyle('Lab', fontName='Helvetica-Bold', fontSize=9, textColor=WHITE, alignment=TA_CENTER, spaceAfter=6)
    big_style = ParagraphStyle('Big', fontName='Helvetica-Bold', fontSize=26, textColor=GOLD, alignment=TA_CENTER, spaceBefore=8, spaceAfter=8, leading=30)
    sub_label_style = ParagraphStyle('SubLab', fontName='Helvetica-Bold', fontSize=8, textColor=WHITE, alignment=TA_CENTER, spaceBefore=4, spaceAfter=12)
    footer_style = ParagraphStyle('Foot', fontName='Helvetica-Bold', fontSize=7, textColor=WHITE, alignment=TA_CENTER, leading=10)

    story = []

    # PAGE 1 - SUMMARY
    story.append(Paragraph("AI-CENTER  //  ROI SUMMARY", title_style))
    story.append(Paragraph(f"GENERATED {datetime.now().strftime('%Y.%m.%d  %H:%M').upper()}  ·  CONFIDENTIAL", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"PROFIT OVER {term_months}-MONTH TERM", label_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"${profit_term:,.0f}", big_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"{purchase_type.upper()}  ·  {capture}% CAPTURE  ·  ${price}/PATIENT", sub_label_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=GOLD, spaceBefore=4, spaceAfter=14))

    data = [
        ["NET PROFIT / MO", f"${net:,.0f}", "PAYBACK", f"{payback:.1f} MO"],
        ["PROFIT YEAR 1", f"${profit_y1:,.0f}", "PROFIT YEAR 2", f"${profit_y2:,.0f}"],
        ["CAPTURED / MO", f"{captured:.0f}", "GROSS REVENUE / MO", f"${gross:,.0f}"],
        ["LEASE PAYMENT", f"${payment:,.2f}" if purchase_type == "Lease" else "—", "TOTAL MONTHLY COST", f"${monthly_cost:,.2f}"],
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
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
    ]))
    story.append(t)
    story.append(Spacer(1, 16))

    story.append(Paragraph("SCENARIO INPUTS", section_style))
    inp = [
        ["DEVICE COST", f"${device_cost:,.0f}", "SETUP / TAX", f"${setup_cost:,.0f}"],
        ["TOTAL INVESTMENT", f"${total_investment:,.0f}", "PURCHASE TYPE", purchase_type.upper()],
        ["INTEREST RATE", f"{interest_rate}%", "TERM", f"{term_months} MONTHS"],
        ["BIOAGE + MAINT", f"${bioage + maint}/MO", "OTHER MONTHLY", f"${other_monthly}/MO"],
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
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t2)
    story.append(Spacer(1, 18))
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
    story.append(HRFlowable(width="100%", thickness=1.5, color=GOLD, spaceAfter=10))

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
        story.append(Spacer(1, 7))

    story.append(Spacer(1, 10))
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
