"""
test_calibrated_tones.py

Plays CALIBRATED tones using sound_elements.py and existing spl_calibration.json.

Purpose:
- Check that the current SPL calibration is correct.
- Uses the same routing and gains as RatVillage (via sound_elements).
- Does NOT modify spl_calibration.json.

Workflow:
1. Open REW -> SPL Meter -> Weighting = Z, Slow.
2. Place UMIK-1 at rat position.
3. Run this script in Spyder.
4. After each calibrated tone, read the SPL and type it (or skip).
"""

import sound_elements as se  # must be in same folder
import pandas as pd
from datetime import datetime

TARGET_DB = 70.0
TONE_DURATION = 5.0

# Same list as current calibration_standalone.py
FREQUENCIES_TO_TEST = [
    # 100, 1368.5
    # 250.0, 290.0, 336.4, 390.2, 452.7, 525.1, 609.1, 706.6,      # Rat reward tones

    # 2000.0, 2320.0, 2691.0, 3122.0, 3621.0,                      # CB Pair 1
    # 4573.0, 5305.0, 6154.0, 7138.0, 8281.0,                      # CB Pair 2
    #10458.0, 12131.0, 14072.0, 16323.0, 18935.0,                 # CB Pair 3
    # 23913.0, 27739.0, 32177.0, 37326.0, 43298.0                  # CB Pair 4
]



def play_calibrated_tone(freq):
    """
    Play a single CALIBRATED tone using the same logic as RatVillage.

    Uses:
    - DEFAULT_FS for freqs <= CROSSOVER_HZ
    - CB_FS for freqs > CROSSOVER_HZ
    - pureToneGen_dB + apply_calibration_gain + Babyface routing
    """
    Fs = se.CB_FS if freq > se.CROSSOVER_HZ else se.DEFAULT_FS
    # This helper already calls pureToneGen_dB + apply_calibration_gain + soundStream.play
    se.play_any_frequency(freq, duration=TONE_DURATION, db=TARGET_DB, FsOut=Fs)


def main():
    print("\n===============================================")
    print(" CALIBRATED SPL TEST TOOL (READ-ONLY)")
    print("===============================================")
    print(f"Using {len(FREQUENCIES_TO_TEST)} test frequencies.")
    print(f"Each tone plays for {TONE_DURATION} seconds.")
    print("After each CALIBRATED tone:")
    print("  Enter SPL value in dB (just for logging)")
    print("  Enter 'r' to repeat")
    print("  Enter nothing to skip")
    print("  Enter 'q' to quit\n")

    measured = {}
    quit_all = False

    for f in FREQUENCIES_TO_TEST:
        if quit_all:
            break

        print(f"\n>>> Playing CALIBRATED {f} Hz …")
        play_calibrated_tone(f)

        while True:
            entry = input(
                f"SPL for calibrated {f} Hz ('r'=repeat, Enter=skip, 'q'=quit): "
            ).strip()

            if entry.lower() == "q":
                quit_all = True
                print("Quitting calibrated test.")
                break

            if entry.lower() == "r":
                print(f"Repeating calibrated {f} Hz …")
                play_calibrated_tone(f)
                continue

            if entry == "":
                print(f"Skipped logging for {f} Hz")
                break

            try:
                spl = float(entry)
                measured[f] = spl
                diff = spl - TARGET_DB
                print(f"Recorded {spl:.1f} dB for {f} Hz  (Δ = {diff:+.1f} dB vs {TARGET_DB} dB)")
                break
            except ValueError:
                print("Invalid input, try again.")
                continue

    if not measured:
        print("\nNo SPL values logged. Calibration file was NOT changed.")
        return

    print("\nSummary of calibrated SPL measurements (no changes written):")
    rows = []
    for f in sorted(measured.keys()):
        spl = measured[f]
        diff = spl - TARGET_DB
        print(f"  {f:7.1f} Hz : {spl:5.1f} dB  (Δ = {diff:+.1f} dB)")
        rows.append({
            "frequency_hz": float(f),
            "measured_db": float(spl),
            "target_db": float(TARGET_DB),
            "delta_db": float(diff)
        })

    print("\nNote: This script does NOT modify spl_calibration.json.")

    # Save summary to Excel
    df = pd.DataFrame(rows)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"calibrated_spl_summary_{timestamp}.xlsx"
    df.to_excel(output_file, index=False)

    print(f"\nSummary saved to Excel: {output_file}")
    print("Note: This script does NOT modify spl_calibration.json.")




if __name__ == "__main__":
    main()
