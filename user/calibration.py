"""
Standalone SPL calibration tool for Babyface Pro FS + RatVillage tones.
Runs in Spyder. Does NOT require academy code.

Workflow:
1. Open REW -> SPL Meter -> Weighting = Z, Slow
2. Place UMIK-1 at rat position
3. Run this script and enter SPL values manually
4. It outputs spl_calibration.json with correction gains

Simple SPL calibration script.
User manually edits FREQUENCIES_TO_TEST.
Uses Babyface Pro FS routing exactly like RatVillage (via sound_elements).
No auto-continue. User enters SPL, repeat last tone, skip, or quit.

This version is in MERGE mode:
- It LOADS existing spl_calibration.json if present
- Updates/overwrites only the frequencies measured in this run
- Keeps all other previously calibrated frequencies
"""

import json
import os
import numpy as np
import sound_elements as se   # must be in same folder

TARGET_DB = 70.0
TONE_DURATION = 5.0
OUTPUT_JSON = "spl_calibration.json"

# ---------------------------------------------------------------
# EDIT THIS LIST MANUALLY
# ---------------------------------------------------------------
FREQUENCIES_TO_TEST = [
    # 100, 1368.5,
    # 250.0, 290.0, 336.4, 390.2, 452.7, 525.1, 609.1, 706.6,      # Rat reward tones

    # 2000.0, 2320.0, 2691.0, 3122.0, 3621.0,                     # CB Pair 1
    # 4573.0, 5305.0, 6154.0, 7138.0, 8281.0,                     # CB Pair 2
    # 10458.0, 12131.0, 14072.0, 16323.0, 18935.0,                # CB Pair 3
    23913.0, 27739.0, 32177.0
    #37326.0, 43298.0                 # CB Pair 4
]

# If True: merge with existing JSON (recommended)
# If False: overwrite JSON with only this run's freqs (original behaviour)
MERGE_MODE = True
CB_FREQS = {f for freqs in se.cb_tones_hz.values() for f in freqs}

# ---------------------------------------------------------------


def play_tone(freq):
    """Play a single tone using the same routing as RatVillage."""
    
    if freq in CB_FREQS:
        Fs = se.CB_FS      # all CB tones at CB_FS
    else:
        Fs = se.DEFAULT_FS # rat freqs and any others at DEFAULT_FS

    tone = se.pureToneGen_dB(freq, TONE_DURATION, db=TARGET_DB, FsOut=Fs)
    se.soundStream.play(tone, FsOut=Fs, freq=freq)


def load_existing_calibration(path):
    """Load existing calibration JSON, or return empty dict if none / invalid."""
    if not os.path.exists(path):
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
        else:
            print(f"Existing {path} is not a dict, ignoring.")
            return {}
    except Exception as e:
        print(f"Could not load existing {path}: {e}. Starting fresh.")
        return {}


def main():
    print("\n===============================================")
    print(" SIMPLE SPL CALIBRATION TOOL (MANUAL LIST)")
    print("===============================================")
    print(f"Using {len(FREQUENCIES_TO_TEST)} test frequencies.")
    print(f"Each tone plays for {TONE_DURATION} seconds.")
    print("After each tone:")
    print("  Enter SPL value in dB")
    print("  Enter 'r' to repeat")
    print("  Enter nothing to skip")
    print("  Enter 'q' to quit\n")

    # Load existing calibration (for merge mode)
    if MERGE_MODE:
        existing_calibration = load_existing_calibration(OUTPUT_JSON)
        print(f"\nMerge mode ON. Loaded {len(existing_calibration)} existing freqs from {OUTPUT_JSON}.\n")
    else:
        existing_calibration = {}
        print("\nMerge mode OFF. Will overwrite any existing calibration file.\n")

    measured = {}
    quit_all = False

    for f in FREQUENCIES_TO_TEST:
        if quit_all:
            break

        print(f"\n>>> Playing {f} Hz …")
        play_tone(f)

        while True:
            entry = input(
                f"SPL for {f} Hz ('r'=repeat, Enter=skip, 'q'=quit): "
            ).strip()

            if entry.lower() == "q":
                quit_all = True
                print("Quitting calibration.")
                break

            if entry.lower() == "r":
                print(f"Repeating {f} Hz …")
                play_tone(f)
                continue

            if entry == "":
                print(f"Skipped {f} Hz")
                break

            try:
                spl = float(entry)
                measured[f] = spl
                print(f"Recorded {spl} dB for {f} Hz")
                break
            except ValueError:
                print("Invalid input, try again.")
                continue

    if not measured:
        print("No new measurements taken. Existing JSON left unchanged.")
        return

    # Compute gain corrections for this run
    new_calibration = {}
    for f, spl in measured.items():
        gain = 10 ** ((TARGET_DB - spl) / 20.0)
        new_calibration[str(float(f))] = {
            "measured_db": spl,
            "gain": gain,
        }

    # Merge logic
    if MERGE_MODE:
        merged = existing_calibration.copy()
        # Overwrite or add entries for the frequencies we just measured
        merged.update(new_calibration)
        final_calibration = merged
    else:
        # Original behaviour: only this run's freqs
        final_calibration = new_calibration

    # Save
    with open(OUTPUT_JSON, "w", encoding="utf-8") as fp:
        json.dump(final_calibration, fp, indent=2)
        
    try:
        import openpyxl
        from openpyxl import Workbook

        wb = Workbook()
        ws = wb.active
        ws.title = "Calibration"

        # Header
        ws.append(["frequency_hz", "measured_db", "gain"])

        # Sort by frequency
        for freq_str in sorted(final_calibration.keys(), key=lambda x: float(x)):
            entry = final_calibration[freq_str]
            ws.append([
                float(freq_str),
                entry.get("measured_db", None),
                entry.get("gain", None),
            ])

        excel_name = "spl_calibration.xlsx"
        wb.save(excel_name)
        print(f"Excel exported to {excel_name}")

    except Exception as e:
        print(f"Could not export Excel file: {e}")


    print("\nCalibration saved to:", OUTPUT_JSON)
    print(f"Total freqs in file: {len(final_calibration)}")
    print("sound_elements.py will automatically load and apply these gains.")


if __name__ == "__main__":
    main()
