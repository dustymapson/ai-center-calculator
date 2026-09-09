import urllib.request

# Last known-good calculator, with a small Cash vs Financed display patch.
_SHA = "4e482597843dce14b3918dba94454e78a24f59cd"
_URL = f"https://raw.githubusercontent.com/dustymapson/ai-center-calculator/{_SHA}/streamlit_app.py"
code = urllib.request.urlopen(_URL, timeout=30).read().decode()

old_card = '''        if purchase_type == "Financed":
            bundle_note = f"Device finance ${device_finance_est:,.0f} + BioAge ${bioage:,.0f} + maint ${maint:,.0f}"
        else:
            bundle_note = f"If financed: device ${device_finance_est:,.0f} + BioAge ${bioage:,.0f} + maint ${maint:,.0f}"
        st.markdown(f"""
        <div class=\"metric-card-hero\">
            <div class=\"label\">Est. Monthly (Device + Software)</div>
            <div class=\"big-number\">${nw500_monthly_est:,.0f}<span style=\"font-size:1rem; font-weight:500; color:#cccccc;\"> / mo</span></div>
            <div style=\"font-size:0.7rem; color:#cccccc; margin-top:0.25rem;\">{bundle_note}</div>
        </div>
        """, unsafe_allow_html=True)'''

new_card = '''        if purchase_type == "Financed":
            bundle_label = "Est. Monthly (Device + Software)"
            bundle_value = nw500_monthly_est
            bundle_note = f"Device finance ${device_finance_est:,.0f} + BioAge ${bioage:,.0f} + maint ${maint:,.0f}"
        else:
            bundle_label = "Monthly Cost (Cash — no loan)"
            bundle_value = software_monthly + other_monthly
            bundle_note = f"BioAge ${bioage:,.0f} + maint ${maint:,.0f} · device paid upfront"
        st.markdown(f"""
        <div class=\"metric-card-hero\">
            <div class=\"label\">{bundle_label}</div>
            <div class=\"big-number\">${bundle_value:,.0f}<span style=\"font-size:1rem; font-weight:500; color:#cccccc;\"> / mo</span></div>
            <div style=\"font-size:0.7rem; color:#cccccc; margin-top:0.25rem;\">{bundle_note}</div>
        </div>
        """, unsafe_allow_html=True)'''

old_pay = '''        <div class=\"metric-value\">{"—" if optos or purchase_type != "Financed" else "$" + f"{payment:,.2f}"}</div>'''
new_pay = '''        <div class=\"metric-value\">{"$0.00" if optos or purchase_type != "Financed" else "$" + f"{payment:,.2f}"}</div>'''

if old_card not in code:
    raise RuntimeError("hero-card patch target not found")
if old_pay not in code:
    raise RuntimeError("finance-payment patch target not found")

code = code.replace(old_card, new_card, 1).replace(old_pay, new_pay, 1)
exec(code)
