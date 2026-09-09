import urllib.request

_SHA = "4e482597843dce14b3918dba94454e78a24f59cd"
_URL = f"https://raw.githubusercontent.com/dustymapson/ai-center-calculator/{_SHA}/streamlit_app.py"
code = urllib.request.urlopen(_URL, timeout=30).read().decode()

patches = []

patches.append((
    '''    st.session_state.last_preset = preset
''',
    '''    st.session_state.device_type = "NW-500"
    st.session_state.purchase_type = "Financed"
    st.session_state.device_cost = 20000
    st.session_state.setup_cost = 6175
    st.session_state.interest_rate = 8.0
    st.session_state.lease_months = 60
    st.session_state._applied_device_type = "NW-500"
    st.session_state.last_preset = preset
''',
))

patches.append((
    '''total_investment = 0 if optos else device_cost + setup_cost
device_finance_est = 0 if optos else monthly_payment(device_cost, interest_rate, lease_months)
payment = 0 if optos or purchase_type != "Financed" else monthly_payment(total_investment, interest_rate, lease_months)

monthly_cost = (bioage + maint + other_monthly) if optos else (payment + bioage + maint + other_monthly)
software_monthly = bioage + maint
nw500_monthly_est = device_finance_est + bioage + maint
''',
    '''total_investment = 0 if optos else device_cost + setup_cost
payment = 0 if optos or purchase_type != "Financed" else monthly_payment(total_investment, interest_rate, lease_months)

monthly_cost = (bioage + maint + other_monthly) if optos else (payment + bioage + maint + other_monthly)
software_monthly = bioage + maint
# Same basis as Total Monthly Cost: financed PMT is on device + setup/tax.
nw500_monthly_est = monthly_cost
device_finance_est = payment
''',
))

patches.append((
    '''    payback = total_investment / net if net > 0 else 999
    payback_label = f"{payback:.1f} mo"
''',
    '''    if net > 0:
        payback = total_investment / net
        payback_label = f"{payback:.1f} mo"
    else:
        payback = None
        payback_label = "N/A"
''',
))

patches.append((
    '''        if purchase_type == "Financed":
            bundle_note = f"Device finance ${device_finance_est:,.0f} + BioAge ${bioage:,.0f} + maint ${maint:,.0f}"
        else:
            bundle_note = f"If financed: device ${device_finance_est:,.0f} + BioAge ${bioage:,.0f} + maint ${maint:,.0f}"
        st.markdown(f"""
        <div class="metric-card-hero">
            <div class="label">Est. Monthly (Device + Software)</div>
            <div class="big-number">${nw500_monthly_est:,.0f}<span style="font-size:1rem; font-weight:500; color:#cccccc;"> / mo</span></div>
            <div style="font-size:0.7rem; color:#cccccc; margin-top:0.25rem;">{bundle_note}</div>
        </div>
        """, unsafe_allow_html=True)
''',
    '''        if purchase_type == "Financed":
            bundle_note = f"Finance ${payment:,.2f} + BioAge ${bioage:,.0f} + maint ${maint:,.0f}" + (f" + other ${other_monthly:,.0f}" if other_monthly else "")
            bundle_caption = "Includes financed payment on device + setup/tax (when financed)."
        else:
            bundle_note = f"No loan · BioAge ${bioage:,.0f} + maint ${maint:,.0f}" + (f" + other ${other_monthly:,.0f}" if other_monthly else "")
            bundle_caption = "Cash: $0 finance. Device paid upfront."
        st.markdown(f"""
        <div class="metric-card-hero">
            <div class="label">Est. Monthly (Device + Software)</div>
            <div class="big-number">${nw500_monthly_est:,.2f}<span style="font-size:1rem; font-weight:500; color:#cccccc;"> / mo</span></div>
            <div style="font-size:0.7rem; color:#cccccc; margin-top:0.25rem;">{bundle_note}</div>
        </div>
        """, unsafe_allow_html=True)
        st.caption(bundle_caption)
''',
))

patches.append((
    '''            pb = total_investment / nt if nt > 0 else 999
            pb_txt = f"{pb:.1f}"
''',
    '''            pb_txt = f"{total_investment / nt:.1f}" if nt > 0 else "N/A"
''',
))

patches.append((
    '''- **NW-500**: device cost starts at $20,000 (editable). Software cost = BioAge + maintenance. The extra card is estimated device finance + BioAge + maintenance.  
''',
    '''- **NW-500**: device cost starts at $20,000 (editable). Software cost = BioAge + maintenance. Est. Monthly (Device + Software) matches Total Monthly Cost (finance payment on device + setup/tax, when financed, plus software and other).  
''',
))

for i, (old, new) in enumerate(patches, 1):
    count = code.count(old)
    if count == 0:
        raise RuntimeError(f"patch {i} target not found")
    code = code.replace(old, new)

if "else 999" in code:
    raise RuntimeError("999 sentinel still present")

exec(code)
