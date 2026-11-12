# Ashura's Light

A Streamlit starter app for comparing lunar south-pole candidate sites using
approximate Sun/Earth elevation series and a simple dust-risk proxy.

## Run locally

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Skyfield downloads the `de421.bsp` ephemeris on first run. The initial site
coordinates and dust-risk calculation are placeholders for development and are
not suitable for mission planning.
