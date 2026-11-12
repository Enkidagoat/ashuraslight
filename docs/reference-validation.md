# Independent geometry reference

**Reference epoch:** 2026-12-01 00:00:00 UTC.  
**Reference implementation:** NAIF CSPICE N0067, used only as a temporary validation oracle; it is not an application dependency.  
**Application implementation:** Skyfield 1.55, with a separate direct vector projection into the `MOON_ME_DE421` body-fixed frame.

The reference was generated with `spkpos(target, et, "MOON_ME_DE421", "NONE", "MOON")` relative to the Moon center, subtracting the site vector computed by CSPICE `georec()` from the PCK lunar reference radius (1737.4 km), then projecting the topocentric vector on the local east/north/up basis. `NONE` is intentional: this validates the stated geometric same-epoch convention and does not include light-time or stellar aberration. Azimuth is clockwise from north in `[0°, 360°)`.

The separate validation run used the same pinned four NAIF files and additionally `naif0012.tls` (SHA-256 `678e32bdb5a744117a467cd9601cd6b373f0e9bc9bbde1371d5eee39600a039b`) only to parse the UTC epoch. Site inputs were the exact published source values recorded in `sites.py`.

| Point | Target | Elevation (°) | Azimuth (°) |
|---|---|---:|---:|
| DM2 / Nobile Rim 2 point 358 | Sun center | -3.012459542225528 | 219.41923412141995 |
| DM2 / Nobile Rim 2 point 358 | Earth center | 1.7962960425281513 | 305.94052773137696 |
| DM1 / Amundsen Rim point 1121 | Sun center | -3.4095917612616016 | 212.8939134967966 |
| DM1 / Amundsen Rim point 1121 | Earth center | 1.246128665641467 | 299.4334054707526 |
| Site07 / Peak Near Shackleton point 1223 | Sun center | 0.5701006426223459 | 154.76784722017246 |
| Site07 / Peak Near Shackleton point 1223 | Earth center | -2.086828930833153 | 241.38456975275744 |

The test tolerance is `1e-6°`; the Skyfield calculation in the isolated verification run agreed to better than that. This is a fixed-case regression check, not a blanket statement about all dates or terrain-aware accuracy.

**Important boundary of this validation:** the candidate-point article publishes DMS coordinates with S/E labels but does not state the point coordinates’ reference frame in its full text. The calculation deliberately tests the project’s provisional assignment of those values to the DE421 ME planetocentric frame. It does not prove that the source coordinates use that datum. Obtain an authoritative source-datum statement or perform a documented transformation before treating the plotted point as absolutely location-verified.

## Validation-only SPICE assets

- `naif0012.tls`: `https://naif.jpl.nasa.gov/pub/naif/generic_kernels/lsk/naif0012.tls` (hash above).
- The four application kernels and their individual hashes are listed in `data/kernels/manifest.json`.
