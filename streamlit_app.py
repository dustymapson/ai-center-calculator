import urllib.request

# Last known-good calculator (Optos software-only + current UI cards).
# Temporary bootloader so the Cloud app is not stuck on a stub.
_SHA = "4e482597843dce14b3918dba94454e78a24f59cd"
_URL = f"https://raw.githubusercontent.com/dustymapson/ai-center-calculator/{_SHA}/streamlit_app.py"
exec(urllib.request.urlopen(_URL, timeout=30).read().decode())
