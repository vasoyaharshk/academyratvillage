"""
Standalone SPL calibration tool for Babyface Pro FS + RatVillage tones.
Runs in Spyder. Does NOT require academy code.

Workflow:
1. Open REW -> SPL Meter -> Weighting = Z, Slow
2. Place UMIK-1 at rat position
3. Run this script and enter SPL values manually
4. It outputs spl_calibration.json with correction gains

"""

import time
import json
import numpy as np
import sound_elements_2 as se   # must be in same folder

TARGET_DB = 70.0               # desired equal SPL
TONE_DURATION = 2.0            # seconds per tone
PAUSE = 1.0                    # gap between tones
OUTPUT_JSON = "spl_calibration.json"


def collect_frequencies():
    freqs = set()

    # rat reward tones
    for f in se.reward_frequency_map.values():
        freqs.add(float(f))

    # CB tones
    for _, flist in se.cb_tones_hz.items():
        for f in flist:
            freqs.add(float(f))

    return sorted(freqs)


def play_tone(freq):
    if freq > se.CROSSOVER_HZ:
        Fs = se.CB_FS
    else:
        Fs = se.DEFAULT_FS

    tone = se.pureToneGen_dB(freq, TONE_DURATION, db=TARGET_DB, FsOut=Fs)
    se.soundStream.play(tone, FsOut=Fs, freq=freq)


def main():
    freqs = collect_frequencies()

    print("\n============================================")
    print(" SPL CALIBRATION TOOL")
    print("============================================")
    print("Open REW SPL Meter. Place UMIK-1 at rat head location.")
    print("Each tone plays for 2 seconds")
    print("Enter measured SPL from REW after each tone")
    print("Type q to quit early, Enter to skip.\n")
    print("Frequencies to test:", freqs)

    measured = {}

    for f in freqs:
        print(f"\n>>> Playing {f} Hz...")
        play_tone(f)
        time.sleep(TONE_DURATION + PAUSE)

        entry = input(f"Enter measured SPL for {f} Hz (or Enter skip, q quit): ").strip()

        if entry.lower() == "q":
            print("Stopping calibration.")
            break
        if entry == "":
            print(f"Skipped {f}")
            continue

        try:
            spl = float(entry)
            measured[f] = spl
        except:
            print("Invalid entry, skipping.")
            continue

    if not measured:
        print("No values recorded — exiting")
        return

    # compute gain corrections
    calibration = {}
    for f, spl in measured.items():
        gain = 10 ** ((TARGET_DB - spl) / 20.0)
        calibration[str(f)] = {"measured_db": spl, "gain": gain}

    with open(OUTPUT_JSON, "w") as fp:
        json.dump(calibration, fp, indent=2)

    print("\nSaved calibration to:", OUTPUT_JSON)
    print("\nIntegrate into sound_elements.py:")
    print("""
with open("spl_calibration.json") as f:
    cal = json.load(f)

gain = cal.get(str(freq), {}).get("gain", 1.0)
tone *= gain
""")



if __name__ == "__main__":
    main()
