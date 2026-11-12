from skyfield.api import load, wgs84

ts = load.timescale()
eph = load("de421.bsp")  # Downloads on first run.

sun = eph["sun"]
earth = eph["earth"]
moon = eph["moon"]


def elevation_series(lat, lon, start, end, body="sun", steps=48):
    """
    Return times and elevation angles (degrees) for Sun or Earth
    as seen from a lunar surface location.
    """
    location = moon + wgs84.latlon(lat, lon)

    # Streamlit date inputs return date objects; construct Skyfield times
    # from their components so both date and datetime inputs work.
    t0 = ts.utc(start.year, start.month, start.day)
    t1 = ts.utc(end.year, end.month, end.day)
    times = ts.linspace(t0, t1, steps)

    target = sun if body == "sun" else earth
    astrometric = location.at(times).observe(target)
    alt, az, distance = astrometric.apparent().altaz()
    return times.utc_datetime(), alt.degrees
