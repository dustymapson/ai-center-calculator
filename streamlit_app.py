import streamlit as st
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.platypus.flowables import Flowable

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

# ---------- SIDEBAR ----------
st.sidebar.markdown("### Scenario Presets")
c1, c2, c3 = st.sidebar.columns(3)
if c1.button("Conservative", use_container_width=True):
    st.session_state.volume = 200
    st.session_state.capture = 35
    st.session_state.price = 29
if c2.button("Base", use_container_width=True):
    st.session_state.volume = 300
    st.session_state.capture = 65
    st.session_state.price = 39
if c3.button("Aggressive", use_container_width=True):
    st.session_state.volume = 400
    st.session_state.capture = 75
    st.session_state.price = 49

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
- 35% = Very Conservative  
- 65% = Typical / Base case  
- 75%+ = Strong trust + optimized workflow  

**Price per Patient** reflects the incremental fee for the AI-Center / BioAge analysis.  

**Net Profit** = Gross revenue − Lease payment − BioAge − Maintenance − Other monthly costs.  

**Not included**: one-time training, marketing, chair-time opportunity cost, or downstream referral revenue.
    """)

# ---------- TRON-THEMED PDF ----------
class DarkBackground(Flowable):
    """Draws a full-page dark background"""
    def __init__(self, width, height):
        Flowable.__init__(self)
        self.width = width
        self.height = height

    def draw(self):
        self.canv.setFillColor(colors.HexColor("#05080f"))
        self.canv.rect(0, 0, self.width, self.height, fill=1, stroke=0)

def create_pdf():
    buffer = BytesIO()
    page_w, page_h = letter

    def draw_tron_background(canvas, doc):
        # Full dark background
        canvas.setFillColor(colors.HexColor("#05080f"))
        canvas.rect(0, 0, page_w, page_h, fill=1, stroke=0)

        # Subtle grid (Tron style)
        canvas.setStrokeColor(colors.HexColor("#0a1a2f"))
        canvas.setLineWidth(0.3)
        for x in range(0, int(page_w), 28):
            canvas.line(x, 0, x, page_h)
        for y in range(0, int(page_h), 28):
            canvas.line(0, y, page_w, y)

        # Top neon line
        canvas.setStrokeColor(colors.HexColor("#00f0ff"))
        canvas.setLineWidth(2)
        canvas.line(40, page_h - 36, page_w - 40, page_h - 36)

        # Bottom neon line
        canvas.line(40, 42, page_w - 40, 42)

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.55*inch,
        leftMargin=0.55*inch,
        topMargin=0.7*inch,
        bottomMargin=0.65*inch
    )

    # Colors
    CYAN = colors.HexColor("#00f0ff")
    CYAN_DIM = colors.HexColor("#00b8d4")
    WHITE = colors.HexColor("#e0f7fa")
    GRAY = colors.HexColor("#78909c")
    DARK_CARD = colors.HexColor("#0a1628")

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'Title', fontName='Helvetica-Bold', fontSize=20,
        textColor=CYAN, spaceAfter=2, alignment=TA_LEFT
    )
    subtitle_style = ParagraphStyle(
        'Subtitle', fontName='Helvetica', fontSize=8,
        textColor=GRAY, spaceAfter=10
    )
    section_style = ParagraphStyle(
        'Section', fontName='Helvetica-Bold', fontSize=10,
        textColor=CYAN, spaceBefore=12, spaceAfter=6
    )
    label_style = ParagraphStyle(
        'Label', fontName='Helvetica', fontSize=8,
        textColor=GRAY, alignment=TA_CENTER
    )
    big_number = ParagraphStyle(
        'Big', fontName='Helvetica-Bold', fontSize=26,
        textColor=CYAN, alignment=TA_CENTER, spaceBefore=4, spaceAfter=4
    )
    normal = ParagraphStyle(
        'Normal', fontName='Helvetica', fontSize=9,
        textColor=WHITE, leading=12
    )
    footer_style = ParagraphStyle(
        'Footer', fontName='Helvetica', fontSize=7,
        textColor=GRAY, alignment=TA_CENTER
    )

    story = []

    # Header
    story.append(Paragraph("AI-CENTER  //  ROI SUMMARY", title_style))
    story.append(Paragraph(
        f"TOPCON HEALTHCARE  ·  GENERATED {datetime.now().strftime('%Y.%m.%d  %H:%M').upper()}  ·  CONFIDENTIAL",
        subtitle_style
    ))

    # Big result
    story.append(Spacer(1, 8))
    story.append(Paragraph(f"PROFIT OVER {term_months}-MONTH TERM", label_style))
    story.append(Paragraph(f"${profit_term:,.0f}", big_number))
    story.append(Paragraph(
        f"{purchase_type.upper()}  ·  {capture}% CAPTURE  ·  ${price}/PATIENT",
        ParagraphStyle('Sub', parent=label_style, fontSize=8, spaceAfter=14)
    ))

    # Neon divider
    story.append(HRFlowable(width="100%", thickness=1.2, color=CYAN, spaceBefore=2, spaceAfter=12))

    # Key metrics
    data = [
        ["NET PROFIT / MO", f"${net:,.0f}", "PAYBACK", f"{payback:.1f} MO"],
        ["PROFIT YEAR 1", f"${profit_y1:,.0f}", "PROFIT YEAR 2", f"${profit_y2:,.0f}"],
        ["CAPTURED / MO", f"{captured:.0f}", "GROSS REVENUE / MO", f"${gross:,.0f}"],
        ["LEASE PAYMENT", f"${payment:,.2f}" if purchase_type == "Lease" else "—", "TOTAL MONTHLY COST", f"${monthly_cost:,.2f}"],
    ]

    t = Table(data, colWidths=[1.65*inch, 1.55*inch, 1.65*inch, 1.55*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), DARK_CARD),
        ('TEXTCOLOR', (0, 0), (0, -1), GRAY),
        ('TEXTCOLOR', (2, 0), (2, -1), GRAY),
        ('TEXTCOLOR', (1, 0), (1, -1), CYAN),
        ('TEXTCOLOR', (3, 0), (3, -1), CYAN),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('FONTNAME', (3, 0), (3, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.6, colors.HexColor("#00f0ff")),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 16))

    # Inputs
    story.append(Paragraph("SCENARIO INPUTS", section_style))
    input_data = [
        ["DEVICE COST", f"${device_cost:,.0f}", "SETUP / TAX", f"${setup_cost:,.0f}"],
        ["TOTAL INVESTMENT", f"${total_investment:,.0f}", "PURCHASE TYPE", purchase_type.upper()],
        ["INTEREST RATE", f"{interest_rate}%", "TERM", f"{term_months} MONTHS"],
        ["BIOAGE SUB", f"${bioage}/MO", "MAINTENANCE", f"${maint}/MO"],
        ["OTHER MONTHLY", f"${other_monthly}/MO", "PATIENT VOLUME", f"{volume}"],
        ["CAPTURE RATE", f"{capture}%", "PRICE / PATIENT", f"${price}"],
    ]
    t2 = Table(input_data, colWidths=[1.65*inch, 1.55*inch, 1.65*inch, 1.55*inch])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), DARK_CARD),
        ('TEXTCOLOR', (0, 0), (0, -1), GRAY),
        ('TEXTCOLOR', (2, 0), (2, -1), GRAY),
        ('TEXTCOLOR', (1, 0), (1, -1), WHITE),
        ('TEXTCOLOR', (3, 0), (3, -1), WHITE),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('FONTNAME', (3, 0), (3, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#00b8d4")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
    ]))
    story.append(t2)
    story.append(Spacer(1, 20))

    # Footer
    story.append(Paragraph(
        "CONFIDENTIAL  //  FOR INTERNAL DISCUSSION ONLY  //  TOPCON HEALTHCARE  //  AI-CENTER<br/>"
        "RESULTS ARE ESTIMATES ONLY AND DO NOT CONSTITUTE FINANCIAL, LEGAL, OR CLINICAL ADVICE",
        footer_style
    ))

    doc.build(story, onFirstPage=draw_tron_background, onLaterPages=draw_tron_background)
    buffer.seek(0)
    return buffer

# ---------- DOWNLOAD BUTTONS ----------
col_dl1, col_dl2 = st.columns(2)

with col_dl1:
    pdf_buffer = create_pdf()
    st.download_button(
        label="Download TRON PDF Summary",
        data=pdf_buffer,
        file_name=f"AI_Center_ROI_TRON_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

with col_dl2:
    text_summary = f"""AI-CENTER ROI SUMMARY
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}
Purchase: {purchase_type} | Volume: {volume} | Capture: {capture}% | Price: ${price}
Device: ${device_cost:,.0f} + Setup ${setup_cost:,.0f} = ${total_investment:,.0f}
Net/mo: ${net:,.0f} | Payback: {payback:.1f} mo | Profit over term: ${profit_term:,.0f}
"""
    st.download_button(
        label="Download Text Summary",
        data=text_summary,
        file_name=f"AI_Center_ROI_Summary_{datetime.now().strftime('%Y%m%d')}.txt",
        mime="text/plain",
        use_container_width=True
    )

st.markdown("---")
st.caption("AI-Center ROI Calculator  ·  Topcon Healthcare  ·  For internal use only  ·  Results are estimates and do not constitute financial advice")
