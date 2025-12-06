#!/usr/bin/env python3
"""
Analyze single-tone WAV files in the folder where this script is saved.

For each .wav file, the script reports:
- frequency_hz: Dominant frequency estimated from FFT (with parabolic refinement)
- duration_ms: Signal duration in milliseconds
- ramp_in_ms / ramp_out_ms: 10–90% raised-cosine-like ramp durations (ms)
- ramp_in_cosine_r / ramp_out_cosine_r: Correlation (0–1) with ideal raised-cosine shape
- rms_dbfs / peak_dbfs: RMS and peak levels in dBFS (0 dBFS = full scale)
- snr_db: Signal-to-noise ratio (dB), using fundamental (+harmonics) vs. rest
- thdn_percent: THD+N as percent of total power (lower is better)
- notes: Warnings or parsing notes

Usage:
- Put this script in a folder with your .wav files and run it.
- Optional args: --bw-hz (bandwidth around each harmonic), --max-harmonics, --csv
"""

import argparse
import math
import os
import sys
import glob
import json
import csv
import numpy as np
from scipy.io import wavfile
from scipy.signal import get_window, hilbert
import pandas as pd


# ----------------------------- Utilities ------------------------------------ #

def read_wav_mono(path):
    fs, x = wavfile.read(path)
    # Normalize to float32 in [-1, 1] if integer type
    if np.issubdtype(x.dtype, np.integer):
        max_int = np.iinfo(x.dtype).max
        x = x.astype(np.float32) / max_int
    else:
        x = x.astype(np.float32)
    # Convert to mono
    if x.ndim == 2:
        x = x.mean(axis=1)
    return fs, x

def duration_ms(x, fs):
    return 1000.0 * len(x) / fs

def dbfs(value):
    value = float(value)
    if value <= 0:
        return -np.inf
    return 20.0 * math.log10(value)

def rms(x):
    return float(np.sqrt(np.mean(np.square(x)))) if len(x) else 0.0

def parabolic_peak(f, x):
    """
    Quadratic (parabolic) interpolation around a peak bin x for spectrum f.
    Returns (vertex_index, vertex_value).
    """
    # Guard edges
    if x <= 0 or x >= len(f) - 1:
        return x, f[x]
    y0, y1, y2 = f[x-1], f[x], f[x+1]
    denom = (y0 - 2*y1 + y2)
    if denom == 0:
        return x, y1
    x_vertex = x + 0.5 * (y0 - y2) / denom
    y_vertex = y1 - 0.25 * (y0 - y2) * (x_vertex - x)
    return x_vertex, y_vertex

def estimate_frequency_hz(x, fs):
    """
    Estimate dominant frequency using windowed FFT and parabolic interpolation.
    """
    # Zero-mean to reduce DC bias
    x = x - np.mean(x)
    n = len(x)
    if n < 8:
        return np.nan
    # Use next power of two for better bin resolution
    nfft = int(2 ** np.ceil(np.log2(n)))
    window = get_window('hann', n, fftbins=True).astype(np.float32)
    xw = np.zeros(nfft, dtype=np.float32)
    xw[:n] = x * window
    spec = np.fft.rfft(xw)
    mag = np.abs(spec)
    # Ignore DC bin for tone detection
    k = np.argmax(mag[1:]) + 1
    k_refined, _ = parabolic_peak(mag, k)
    freq = k_refined * fs / nfft
    return float(freq)

def moving_average(a, w):
    if w <= 1:
        return a
    c = np.cumsum(np.insert(a, 0, 0.0))
    out = (c[w:] - c[:-w]) / float(w)
    # pad to original length
    pad_left = w//2
    pad_right = len(a) - len(out) - pad_left
    return np.pad(out, (pad_left, pad_right), mode='edge')

def estimate_envelope(x, fs, smooth_ms=2.0):
    """
    Amplitude envelope via Hilbert transform, with simple moving-average smoothing.
    """
    if len(x) == 0:
        return np.array([], dtype=np.float32)
    analytic = hilbert(x)
    env = np.abs(analytic).astype(np.float32)
    win = max(1, int(fs * (smooth_ms / 1000.0)))
    env_sm = moving_average(env, win).astype(np.float32)
    return env_sm

def central_level(env, trim_frac=0.2):
    """
    Robust steady-state level estimate: median of the central band (exclude edges).
    """
    n = len(env)
    if n == 0:
        return 0.0
    a = int(n * trim_frac)
    b = n - a
    if b <= a:
        return float(np.median(env))
    return float(np.median(env[a:b]))

def find_threshold_crossing(env, target, direction="up"):
    """
    Find the first index where env crosses target upwards or downwards.
    Returns index or None.
    """
    if len(env) == 0:
        return None
    if direction == "up":
        idx = np.where(env >= target)[0]
    else:
        idx = np.where(env <= target)[0]
    return int(idx[0]) if idx.size else None

def ramp_metrics(env, fs, steady_level, lo=0.10, hi=0.90, edge="in"):
    """
    Compute 10–90% ramp duration in ms and correlation with an ideal raised-cosine ramp.
    edge: "in" for attack, "out" for release (search from end).
    Returns (ramp_ms, cosine_r)
    """
    if len(env) < 10 or steady_level <= 0:
        return np.nan, np.nan

    if edge == "in":
        ref = env
        start_level = lo * steady_level
        end_level   = hi * steady_level
        i_lo = find_threshold_crossing(ref, start_level, "up")
        i_hi = find_threshold_crossing(ref, end_level, "up")
    else:
        ref = env[::-1]  # analyze from the end backwards
        start_level = lo * steady_level
        end_level   = hi * steady_level
        i_lo = find_threshold_crossing(ref, start_level, "up")
        i_hi = find_threshold_crossing(ref, end_level, "up")

    if i_lo is None or i_hi is None or i_hi <= i_lo:
        return np.nan, np.nan

    ramp_len = i_hi - i_lo + 1
    seg = ref[i_lo:i_hi+1].astype(np.float32)

    # Normalize segment to [0,1]
    seg_n = (seg - seg[0]) / max(1e-12, (seg[-1] - seg[0]))

    # Ideal raised-cosine from 0 to 1 over the same number of samples:
    n = len(seg_n)
    t = np.arange(n, dtype=np.float32)
    ideal = 0.5 * (1 - np.cos(np.pi * (t / (n - 1)))) if n > 1 else np.array([0.0], dtype=np.float32)

    # Pearson correlation
    seg_n_z = (seg_n - np.mean(seg_n))
    ideal_z = (ideal - np.mean(ideal))
    denom = (np.linalg.norm(seg_n_z) * np.linalg.norm(ideal_z))
    r = float(np.dot(seg_n_z, ideal_z) / denom) if denom > 0 else np.nan

    ramp_ms = 1000.0 * ramp_len / fs
    return float(ramp_ms), r

def harmonic_bins(fs, nfft, f0, bw_hz, max_harmonics):
    """
    Produce index ranges (start, stop) for fundamental and its harmonics within ±bw_hz.
    """
    if not np.isfinite(f0) or f0 <= 0:
        return []
    bins = []
    for h in range(1, max_harmonics + 1):
        fh = h * f0
        if fh >= fs / 2:
            break
        k_center = fh * nfft / fs
        k_bw = max(1.0, bw_hz * nfft / fs)
        k0 = int(max(0, np.floor(k_center - k_bw)))
        k1 = int(min(nfft//2, np.ceil(k_center + k_bw)))
        if k1 > k0:
            bins.append((k0, k1))
    return bins

def snr_and_thdn(x, fs, f0, bw_hz=5.0, max_harmonics=5):
    """
    Compute SNR (dB) and THD+N (%) using bands around fundamental and harmonics.
    """
    x = x - np.mean(x)
    n = len(x)
    if n < 8 or not np.isfinite(f0) or f0 <= 0:
        return np.nan, np.nan

    nfft = int(2 ** np.ceil(np.log2(n)))
    window = get_window('hann', n, fftbins=True).astype(np.float32)
    xw = np.zeros(nfft, dtype=np.float32)
    xw[:n] = x * window
    spec = np.fft.rfft(xw)
    power = (np.abs(spec) ** 2).astype(np.float64)

    # Total power excluding DC bin:
    total = np.sum(power[1:])

    # Signal power in harmonic bands
    bands = harmonic_bins(fs, nfft, f0, bw_hz, max_harmonics)
    mask = np.zeros_like(power, dtype=bool)
    for (a, b) in bands:
        mask[a:b+1] = True

    signal_power = float(np.sum(power[mask]))
    noise_power  = float(max(0.0, total - signal_power))

    if signal_power <= 0 or total <= 0:
        return np.nan, np.nan

    snr_db = 10.0 * math.log10(signal_power / max(1e-20, noise_power))
    thdn_percent = 100.0 * (noise_power / total)
    return float(snr_db), float(thdn_percent)

# ----------------------------- Main analysis -------------------------------- #

def analyze_file(path, args):
    result = {
        "file": os.path.basename(path),
        "sample_rate": np.nan,   # NEW
        "frequency_hz": np.nan,
        "duration_ms": np.nan,
        "ramp_in_ms": np.nan,
        "ramp_in_cosine_r": np.nan,
        "ramp_out_ms": np.nan,
        "ramp_out_cosine_r": np.nan,
        "rms_dbfs": np.nan,
        "peak_dbfs": np.nan,
        "snr_db": np.nan,
        "thdn_percent": np.nan,
        "notes": ""
    }

    try:
        fs, x = read_wav_mono(path)
        result["sample_rate"] = fs   # record sample rate
        if len(x) == 0:
            result["notes"] = "Empty audio."
            return result

        # Duration
        dur_ms = duration_ms(x, fs)
        result["duration_ms"] = round(dur_ms, 3)

        # Levels (dBFS)
        x_absmax = float(np.max(np.abs(x)))
        x_rms = rms(x)
        result["peak_dbfs"] = round(dbfs(x_absmax), 3)
        result["rms_dbfs"]  = round(dbfs(x_rms), 3)

        # Frequency
        f0 = estimate_frequency_hz(x, fs)
        result["frequency_hz"] = round(f0, 3) if np.isfinite(f0) else np.nan

        # Envelope & ramps
        env = estimate_envelope(x, fs, smooth_ms=2.0)
        level = central_level(env, trim_frac=0.2)
        rin_ms, rin_r = ramp_metrics(env, fs, level, lo=0.10, hi=0.90, edge="in")
        rout_ms, rout_r = ramp_metrics(env, fs, level, lo=0.10, hi=0.90, edge="out")
        result["ramp_in_ms"] = round(rin_ms, 3) if np.isfinite(rin_ms) else np.nan
        result["ramp_in_cosine_r"] = round(rin_r, 3) if np.isfinite(rin_r) else np.nan
        result["ramp_out_ms"] = round(rout_ms, 3) if np.isfinite(rout_ms) else np.nan
        result["ramp_out_cosine_r"] = round(rout_r, 3) if np.isfinite(rout_r) else np.nan
        
                # Convert 10–90% ramp to full cosine ramp (0–100%)
        if np.isfinite(rin_ms):
            full_ramp_in = rin_ms / 0.616
        else:
            full_ramp_in = np.nan
        
        if np.isfinite(rout_ms):
            full_ramp_out = rout_ms / 0.616
        else:
            full_ramp_out = np.nan
        
        result["ramp_in_full_ms"] = round(full_ramp_in, 3)
        result["ramp_out_full_ms"] = round(full_ramp_out, 3)

        # Quality metrics
        snr_db, thdn_pct = snr_and_thdn(x, fs, f0, bw_hz=args.bw_hz, max_harmonics=args.max_harmonics)
        result["snr_db"] = round(snr_db, 3) if np.isfinite(snr_db) else np.nan
        result["thdn_percent"] = round(thdn_pct, 4) if np.isfinite(thdn_pct) else np.nan

        # Notes
        notes = []
        if x_absmax >= 0.999:
            notes.append("Clipping risk (peak near 0 dBFS).")
        if not np.isfinite(f0) or f0 <= 0:
            notes.append("Frequency estimation failed.")
        if np.isnan(result["ramp_in_ms"]) or np.isnan(result["ramp_out_ms"]):
            notes.append("Ramp estimation unstable (very short or noisy).")
        result["notes"] = " ".join(notes)

    except Exception as e:
        result["notes"] = f"Error: {e}"

    return result

def main():
    parser = argparse.ArgumentParser(description="Analyze single-tone WAV files in the current folder.")
    parser.add_argument("--pattern", default="*.wav", help="Glob pattern for audio files (default: *.wav)")
    parser.add_argument("--bw-hz", type=float, default=5.0, help="Half-bandwidth (Hz) around each harmonic for SNR/THD+N (default: 5.0)")
    parser.add_argument("--max-harmonics", type=int, default=5, help="Max harmonics to include (default: 5)")
    parser.add_argument("--csv", default=None, help="Optional output CSV filename")
    args = parser.parse_args()

    folder = os.path.dirname(os.path.abspath(__file__))
    files = sorted(glob.glob(os.path.join(folder, args.pattern)))
    if not files:
        print("No files found matching pattern:", args.pattern, file=sys.stderr)
        sys.exit(1)

    results = []
    for f in files:
        res = analyze_file(f, args)
        results.append(res)

    # Pretty table to stdout
    headers = [
        "file", "sample_rate", "frequency_hz", "duration_ms",
        "ramp_in_ms", "ramp_in_full_ms", "ramp_in_cosine_r",
        "ramp_out_ms", "ramp_out_full_ms", "ramp_out_cosine_r",
        "rms_dbfs", "peak_dbfs",
        "snr_db", "thdn_percent", "notes"
    ]
    # Print header
    print("\t".join(headers))
    for r in results:
        row = [str(r.get(h, "")) for h in headers]
        print("\t".join(row))

    # Always save CSV when running in Spyder
    output_csv = "results.csv"
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for r in results:
            writer.writerow({h: r.get(h, "") for h in headers})
    print(f"Saved results to {output_csv}")
    

    SPL_REF = 70.0              # dB SPL for 14072_70.wav
    REF_FILE = "14072_calib.wav"   # your reference filename
    
    df = pd.read_csv("results.csv")
    
    ref_row = df[df["file"] == REF_FILE].iloc[0]
    rms_dbfs_ref = ref_row["rms_dbfs"]
    
    df["SPL_estimated"] = SPL_REF + (df["rms_dbfs"] - rms_dbfs_ref)
    
    df.to_csv("results_with_SPL.csv", index=False)
    print("Saved results_with_SPL.csv with SPL_estimated column.")

    
if __name__ == "__main__":
    main()
