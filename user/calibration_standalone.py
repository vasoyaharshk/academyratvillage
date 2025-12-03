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
"""

import json
import numpy as np
import sound_elements as se   # must be in same folder

TARGET_DB = 70.0
TONE_DURATION = 5.0
OUTPUT_JSON = "spl_calibration.json"

# ---------------------------------------------------------------
# EDIT THIS LIST MANUALLY
# ---------------------------------------------------------------
FREQUENCIES_TO_TEST = [
    250.0, 290.0, 336.4, 390.2, 452.7, 525.1, 609.1, 706.6,      # Rat reward tones

    #2000.0, 2320.0, 2691.0, 3122.0, 3621.0,                      # CB Pair 1
    #4573.0, 5305.0, 6154.0, 7138.0, 8281.0,                      # CB Pair 2
    #10458.0, 12131.0, 14072.0, 16323.0, 18935.0,                 # CB Pair 3
]

# ---------------------------------------------------------------


def play_tone(freq):
    """Play a single tone using the same routing as RatVillage."""
    Fs = se.CB_FS if freq > se.CROSSOVER_HZ else se.DEFAULT_FS
    tone = se.pureToneGen_dB(freq, TONE_DURATION, db=TARGET_DB, FsOut=Fs)
    se.soundStream.play(tone, FsOut=Fs, freq=freq)


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
        print("No measurements taken.")
        return

    # Compute gain corrections
    calibration = {}
    for f, spl in measured.items():
        gain = 10 ** ((TARGET_DB - spl) / 20.0)
        calibration[str(f)] = {"measured_db": spl, "gain": gain}

    with open(OUTPUT_JSON, "w") as fp:
        json.dump(calibration, fp, indent=2)

    print("\nCalibration saved to:", OUTPUT_JSON)
    print("sound_elements.py will automatically load and apply these gains.")


if __name__ == "__main__":
    main()
