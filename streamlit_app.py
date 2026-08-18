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

    # ========== PAGE 1: SUMMARY ==========
    story.append(Paragraph("AI-CENTER  //  ROI SUMMARY", title_style))
    story.append(Paragraph(f"GENERATED {datetime.now().strftime('%Y.%m.%d  %H:%M').upper()}  ·  CONFIDENTIAL", subtitle_style))
    
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"PROFIT OVER {term_months}-MONTH TERM", label_style))
    story.append(Paragraph(f"${profit_term:,.0f}", big_style))
    story.append(Paragraph(f"{purchase_type.upper()}  ·  {capture}% CAPTURE  ·  ${price}/PATIENT", sub_label_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=GOLD, spaceBefore=2, spaceAfter=10))

    # Key results
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

    # ----- NEW: Monthly Cost Breakdown -----
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

    # ========== PAGE 2: PRO FORMA MATRIX ==========
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
