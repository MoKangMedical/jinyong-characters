#!/usr/bin/env python3
"""Batch generate audio for Jinyong character courses using Moss-TTS-Nano.
Reads narration texts from extracted_data.json, generates WAV files,
converts to MP3 via ffmpeg, outputs to docs/audio/.

Usage:
  cd ~/Desktop/OPC/jinyong-characters
  python scripts/gen_audio_moss.py              # all 151 characters
  python scripts/gen_audio_moss.py --limit 10    # first 10 only
  python scripts/gen_audio_moss.py --voice Junhao    # built-in voice
  python scripts/gen_audio_moss.py --prompt-audio /path/to/ref.wav  # voice cloning
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

# --- CONFIG ---
PROJECT_DIR = Path(os.path.expanduser("~/Desktop/OPC/jinyong-characters"))
MOSS_DIR = Path(os.path.expanduser("~/Desktop/OPC/moss-tts-nano"))
DATA_FILE = PROJECT_DIR / "extracted_data.json"
AUDIO_DIR = PROJECT_DIR / "docs" / "audio"
TEMP_DIR = MOSS_DIR / "generated_audio"

# Moss-TTS-Nano settings
VOICE = "Junhao"          # built-in voice preset
PROMPT_AUDIO = None        # set to Path for voice cloning mode
SAMPLE_MODE = "fixed"      # greedy | fixed | full
CPU_THREADS = 4
MAX_NEW_FRAMES = 500       # ~20s at 48kHz 25fps

# ffmpeg settings
MP3_BITRATE = "128k"

# Rate limiting
SLEEP_BETWEEN = 2  # seconds between generations to prevent overheating


def run_moss_tts(text: str, output_wav: str, voice: str = "Junhao", prompt_audio: Path = None) -> bool:
    """Run Moss-TTS-Nano to synthesize a single text."""
    cmd = [
        sys.executable, str(MOSS_DIR / "infer_onnx.py"),
        "--text", text,
        "--voice", voice,
        "--output-audio-path", output_wav,
        "--sample-mode", SAMPLE_MODE,
        "--cpu-threads", str(CPU_THREADS),
        "--max-new-frames", str(MAX_NEW_FRAMES),
    ]
    if prompt_audio:
        cmd.extend(["--prompt-audio-path", str(prompt_audio)])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True, text=True,
            timeout=300,
            cwd=str(MOSS_DIR),
        )
        if result.returncode != 0:
            print(f"  ERROR: Moss-TTS failed (rc={result.returncode})")
            print(f"  STDERR: {result.stderr[-500:]}")
            return False
        # Check output file exists and is non-empty
        if not os.path.exists(output_wav) or os.path.getsize(output_wav) < 1000:
            print(f"  ERROR: Output WAV missing or too small: {output_wav}")
            return False
        return True
    except subprocess.TimeoutExpired:
        print(f"  ERROR: Moss-TTS timed out (300s)")
        return False


def convert_to_mp3(wav_path: str, mp3_path: str) -> bool:
    """Convert WAV to MP3 using ffmpeg."""
    cmd = [
        "ffmpeg", "-y", "-i", wav_path,
        "-codec:a", "libmp3lame",
        "-b:a", MP3_BITRATE,
        mp3_path,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            print(f"  ERROR: ffmpeg failed: {result.stderr[-300:]}")
            return False
        if not os.path.exists(mp3_path) or os.path.getsize(mp3_path) < 500:
            print(f"  ERROR: MP3 missing or too small: {mp3_path}")
            return False
        return True
    except subprocess.TimeoutExpired:
        print(f"  ERROR: ffmpeg timed out")
        return False


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Batch Moss-TTS-Nano audio generation")
    parser.add_argument("--limit", type=int, default=0, help="Only process first N characters")
    parser.add_argument("--start", type=int, default=0, help="Start from index N")
    parser.add_argument("--voice", type=str, default="Junhao", help="Built-in voice preset")
    parser.add_argument("--prompt-audio", type=str, default=None, help="Reference audio for voice cloning")
    parser.add_argument("--dry-run", action="store_true", help="List characters without generating")
    args = parser.parse_args()

    voice = args.voice
    prompt_audio = None
    if args.prompt_audio:
        prompt_audio = Path(args.prompt_audio)
        if not prompt_audio.exists():
            print(f"ERROR: Reference audio not found: {prompt_audio}")
            sys.exit(1)

    # Load narration data
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    narrations = data.get("narrations", {})
    if not narrations:
        print("ERROR: No narrations found in extracted_data.json")
        sys.exit(1)

    char_ids = list(narrations.keys())
    if args.limit > 0:
        char_ids = char_ids[args.start:args.start + args.limit]
    elif args.start > 0:
        char_ids = char_ids[args.start:]

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    mode = "voice-cloning" if PROMPT_AUDIO else f"built-in({VOICE})"
    print(f"Moss-TTS-Nano Batch Audio Generator")
    print(f"  Mode: {mode}")
    print(f"  Total characters: {len(char_ids)}")
    print(f"  Output dir: {AUDIO_DIR}")
    print()

    if args.dry_run:
        for i, cid in enumerate(char_ids):
            text = narrations[cid]
            print(f"  [{i+1}/{len(char_ids)}] {cid}: {text[:80]}...")
        return

    success = 0
    fail = 0
    skipped = 0
    t_start = time.time()

    for i, char_id in enumerate(char_ids):
        text = narrations[char_id]
        mp3_path = AUDIO_DIR / f"{char_id}.mp3"
        wav_path = TEMP_DIR / f"{char_id}.wav"

        # Skip if already generated
        if mp3_path.exists() and mp3_path.stat().st_size > 500:
            skipped += 1
            if i < 3:
                print(f"  [{i+1}/{len(char_ids)}] {char_id}: SKIP (exists)")
            continue

        elapsed = time.time() - t_start
        eta = (elapsed / max(i - skipped, 1)) * (len(char_ids) - i) if i > skipped else 0
        print(f"  [{i+1}/{len(char_ids)}] {char_id}: {text[:60]}...  (elapsed={elapsed:.0f}s, ETA={eta:.0f}s)")

        # Step 1: Generate WAV with Moss-TTS
        if not run_moss_tts(text, str(wav_path), voice, prompt_audio):
            fail += 1
            continue

        # Step 2: Convert to MP3
        if not convert_to_mp3(str(wav_path), str(mp3_path)):
            fail += 1
            continue

        # Clean up WAV
        try:
            os.remove(str(wav_path))
        except OSError:
            pass

        success += 1

        # Rate limit
        if i < len(char_ids) - 1:
            time.sleep(SLEEP_BETWEEN)

    total_time = time.time() - t_start
    print()
    print(f"=" * 60)
    print(f"COMPLETE: {success} success, {fail} failed, {skipped} skipped")
    print(f"Total time: {total_time:.0f}s ({total_time/60:.1f}m)")
    print(f"Avg per char: {total_time/max(success,1):.1f}s")
    print(f"Output: {AUDIO_DIR}")

    if fail > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
