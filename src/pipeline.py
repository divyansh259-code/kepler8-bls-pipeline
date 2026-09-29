import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import lightkurve as lk
from astropy.timeseries import BoxLeastSquares

# 1. Download and clean Kepler-8 light curve data
search_result = lk.search_lightcurve("Kepler-8", author="Kepler", cadence="long")
print("Search Result:", search_result)

lc_collection = search_result.download_all()
stitched_lc = lc_collection.stitch()
clean_lc = stitched_lc.remove_nans()
normalized_lc = clean_lc.normalize()

timearray = normalized_lc.time.value
fluxarray = normalized_lc.flux.value

# 2. Run Box Least Squares (BLS)
bls = BoxLeastSquares(timearray, fluxarray)
timeperiod = np.linspace(1, 10, 10000)
durations_to_try = np.linspace(0.05, 0.3, 10)
result = bls.power(timeperiod, durations_to_try)

best_index = np.argmax(result.power)
best_period = result.period[best_index]
best_duration = result.duration[best_index]
best_t0 = result.transit_time[best_index]
best_depth = result.depth[best_index]

# Convert Kepler mission time (BKJD) to standard BJD
bjd_offset = 2454833.0
best_t0_bjd = best_t0 + bjd_offset
radius_ratio = np.sqrt(best_depth)

print(f"Best Period: {best_period:.5f} days")
print(f"Best Duration: {best_duration:.4f} days ({best_duration * 24:.2f} hrs)")
print(f"Best Transit Time (T0): {best_t0:.5f} BKJD | {best_t0_bjd:.5f} BJD")
print(f"Best Depth: {best_depth:.6f} (~{best_depth * 100:.3f}%)")
print(f"Radius Ratio (Rp/R*): {radius_ratio:.4f}")

print(f"best period: {best_period}, Best Duration: {best_duration}, Best Transit Time: {best_t0}, Best Depth: {best_depth}")
print(durations_to_try)

# 3. Plot and save BLS Periodogram
plt.figure()
plt.plot(result.period, result.power)
plt.xlabel("Period (days)")
plt.ylabel("BLS Power")
plt.tight_layout()
plt.savefig("assets/bls_periodogram.png", dpi=300)
plt.close()

# 4. Phase-fold and save light curve
phase = ((timearray - best_t0 + best_period / 2) % best_period) - best_period / 2

plt.figure()
plt.scatter(phase, fluxarray, s=2, color="black", alpha=0.5)
plt.xlabel("Phase (days)")
plt.ylabel("Normalized Flux")
plt.title("Phase-Folded Light Curve")
plt.xlim(-0.3, 0.3)
plt.tight_layout()
plt.savefig("assets/phase_folded_transit.png", dpi=300)
plt.close()

print("Plots successfully saved to assets/")
