# voice_output.py
# Description: Sends system summary content to Applio-RVC for speech generation and playback

import os
import subprocess

PC_NAME = os.environ.get("COMPUTERNAME", "UNKNOWN")
BASE_REPORT_DIR = os.path.expandvars(r"%USERPROFILE%\Documents\System Reports")
REPORT_PATH = os.path.join(BASE_REPORT_DIR, PC_NAME)

# Path to your RVC TTS output script (update this to your environment)
APPLIO_RVC_SCRIPT = r"C:\AI\RVC\inference\generate_voice.py"
OUTPUT_AUDIO_PATH = r"C:\AI\RVC\output\spoken_summary.wav"


def extract_summary_for_speech(report_file_path):
    """
    Read the report and extract the summary (not full logs) for voice output.
    """
    summary_lines = []
    with open(report_file_path, 'r', encoding='utf-8') as file:
        include = False
        for line in file:
            if line.startswith("Top 5 frequent ERRORs"):
                include = True
            if include:
                summary_lines.append(line.strip())
    return " ".join(summary_lines)


def speak_text_via_rvc(text):
    """
    Call Applio-RVC TTS inference with the given text.
    """
    command = [
        "python", APPLIO_RVC_SCRIPT,
        "--text", text,
        "--output", OUTPUT_AUDIO_PATH
    ]
    subprocess.run(command, check=True)


def speak_latest_report():
    """
    Find the latest report and send its summary to be spoken aloud.
    """
    reports = [f for f in os.listdir(REPORT_PATH) if f.endswith(".txt") and PC_NAME in f]
    if not reports:
        print("No reports found to read aloud.")
        return

    latest_report = max(reports, key=lambda f: os.path.getmtime(os.path.join(REPORT_PATH, f)))
    full_path = os.path.join(REPORT_PATH, latest_report)
    print(f"🔊 Speaking summary of {latest_report}")
    summary_text = extract_summary_for_speech(full_path)
    speak_text_via_rvc(summary_text)


if __name__ == '__main__':
    speak_latest_report()
