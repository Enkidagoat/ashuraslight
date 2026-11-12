from __future__ import annotations

from datetime import date
import os
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

from ephemeris import (
    MAX_SUPPORTED_DATE,
    MIN_SUPPORTED_DATE,
    EphemerisDataError,
    GeometryInputError,
    LunarGeometry,
    build_hourly_utc_grid,
)
from sites import FRAME_INTERPRETATION, get_site_list

PROJECT_ROOT = Path(__file__).resolve().parent
KERNEL_DIR = Path(os.environ.get("ASHURASLIGHT_KERNEL_DIR", PROJECT_ROOT / "data" / "kernels"))

st.set_page_config(page_title="Ashura’s Light — Lunar Geometry", layout="wide")
st.title("Ashura’s Light")
st.caption("Geometric lunar Sun and Earth elevation comparison")
st.info(
    "These plots show the geometric elevation of the Sun’s and Earth’s centers above a "
    "smooth local horizon. Local terrain blockage, the apparent disks, and atmospheric "
    "refraction are not modeled. Earth elevation does not guarantee communications "
    "availability; Sun-center elevation is not a full illumination or power assessment. "
    "No dust model is included."
)
st.warning(FRAME_INTERPRETATION)

sites = get_site_list()
site_labels = {site.name: site for site in sites}

with st.sidebar:
    st.header("Comparison")
    selected_names = st.multiselect(
        "Published candidate points",
        options=list(site_labels),
        default=list(site_labels)[:2],
        help="Select at least two cited comparison points from candidate regions.",
    )
    start_date = st.date_input(
        "Start date (UTC)",
        value=date(2026, 12, 1),
        min_value=MIN_SUPPORTED_DATE,
        max_value=MAX_SUPPORTED_DATE,
    )
    end_date = st.date_input(
        "End date (UTC, inclusive)",
        value=date(2026, 12, 3),
        min_value=MIN_SUPPORTED_DATE,
        max_value=MAX_SUPPORTED_DATE,
    )
    calculate = st.button("Calculate comparison", type="primary", use_container_width=True)

with st.expander("Site coordinate provenance and assumptions"):
    for site in sites:
        st.markdown(
            f"**{site.name}** (`{site.site_id}`): {site.source_coordinate_text}; "
            f"planetocentric latitude, signed east-positive longitude, frame "
            f"`{site.reference_frame}`, reference-surface elevation assumption "
            f"{site.elevation_m:.1f} m. [Source study]({site.source_url})."
        )


def add_series(fig: go.Figure, x, y, name: str) -> None:
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name=name))


if calculate:
    if len(selected_names) < 2:
        st.error("Select at least two published candidate points to compare.")
    else:
        geometry = None
        try:
            timestamps = build_hourly_utc_grid(start_date, end_date)
            geometry = LunarGeometry(KERNEL_DIR)
            results = [geometry.calculate_site(site_labels[name], timestamps) for name in selected_names]
        except (GeometryInputError, EphemerisDataError, KeyError, OSError) as exc:
            st.error(str(exc))
        else:
            sun_fig = go.Figure()
            earth_fig = go.Figure()
            for result in results:
                add_series(sun_fig, result.timestamps_utc, result.sun_elevation_deg, result.site.name)
                add_series(earth_fig, result.timestamps_utc, result.earth_elevation_deg, result.site.name)
            for fig, title in (
                (sun_fig, "Sun-center elevation"),
                (earth_fig, "Earth-center elevation"),
            ):
                fig.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="0° horizon")
                fig.update_layout(
                    title=title,
                    xaxis_title="UTC",
                    yaxis_title="Geometric elevation (degrees)",
                    hovermode="x unified",
                    height=420,
                    legend_title="Published candidate point",
                )
                st.plotly_chart(fig, use_container_width=True)
            st.caption(
                f"{len(timestamps)} deterministic hourly UTC samples, including every hour "
                f"from 00:00 on {start_date.isoformat()} through 23:00 on {end_date.isoformat()}. "
                "No interpolation was applied."
            )
        finally:
            if geometry is not None:
                geometry.close()
