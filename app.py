import streamlit as st
import plotly.graph_objects as go
from datetime import date, timedelta

from sites import get_site_list, get_coords
from ephemeris import elevation_series
from dust_model import simple_dust_risk

st.set_page_config(page_title="Ashura's Light – Lunar Landing Site Navigator", layout="wide")
st.title("Ashura's Light")
st.caption("Lunar Landing Site Navigator – Sun & Earth windows + dust risk proxy")

# Sidebar controls
sites = get_site_list()
selected = st.sidebar.multiselect("Select sites to compare", sites, default=sites[:2])
days = st.sidebar.slider("Days to simulate", 3, 30, 14)
start_date = st.sidebar.date_input("Start date", date(2026, 12, 1))
mitigation = st.sidebar.slider("Electrostatic mitigation effectiveness", 0.0, 1.0, 0.3)

if st.sidebar.button("Calculate"):
    end_date = start_date + timedelta(days=days)

    for name in selected:
        lat, lon = get_coords(name)
        times, sun_alt = elevation_series(lat, lon, start_date, end_date, body="sun")
        _, earth_alt = elevation_series(lat, lon, start_date, end_date, body="earth")

        risk = simple_dust_risk(sun_alt, mitigation_factor=mitigation)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=times, y=sun_alt, name="Sun elevation"))
        fig.add_trace(go.Scatter(x=times, y=earth_alt, name="Earth elevation"))
        fig.add_trace(
            go.Scatter(
                x=times,
                y=risk * 90,
                name="Dust risk proxy (scaled)",
                line=dict(dash="dot"),
            )
        )
        fig.update_layout(
            title=f"{name} ({lat:.2f}°, {lon:.2f}°)",
            yaxis_title="Elevation / Risk",
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)
