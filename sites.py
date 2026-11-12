# Pre-loaded lunar south-pole candidate sites (approximate coordinates)
# Format: name, latitude (deg), longitude (deg)

CANDIDATE_SITES = {
    "Shackleton Rim (approx)": (-89.9, 0.0),
    "de Gerlache Rim": (-88.5, 270.0),
    "Haworth": (-86.8, 0.0),
    "Malapert Massif": (-86.0, 0.0),
    "Connecting Ridge": (-89.0, 220.0),
}


def get_site_list():
    return sorted(CANDIDATE_SITES)


def get_coords(name: str):
    if not isinstance(name, str):
        return None

    normalized = name.strip()
    if not normalized:
        return None

    if normalized in CANDIDATE_SITES:
        return CANDIDATE_SITES[normalized]

    lowered = normalized.lower()
    for site_name, coords in CANDIDATE_SITES.items():
        if site_name.lower() == lowered:
            return coords

    return None
