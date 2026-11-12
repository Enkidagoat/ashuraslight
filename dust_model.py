import numpy as np


def simple_dust_risk(sun_elevations, mitigation_factor=0.0):
    """
    Very rough proxy:
    - Longer periods above horizon → more photoemission / charging cycles
    - mitigation_factor 0–1 reduces the effective risk (simulates electrostatic cleaning)
    """
    illuminated = sun_elevations > 0
    # cumulative "charging exposure"
    exposure = np.cumsum(illuminated.astype(float))
    risk = exposure / (np.max(exposure) + 1e-6)
    effective_risk = risk * (1.0 - mitigation_factor)
    return effective_risk
