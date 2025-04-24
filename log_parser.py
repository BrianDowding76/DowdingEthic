# log_parser.py
# Part of the DowdingEthic assistant system
# Description: Collects and summarizes critical Windows logs for daily reporting

import os
import datetime
import win32evtlog
import win32evtlogutil
import win32con
from collections import Counter

PC_NAME = os.environ.get("COMPUTERNAME", "UNKNOWN")
BASE_REPORT_DIR = os.path.expandvars(r"%USERPROFILE%\Documents\System Reports")
REPORT_DIR = os.path.join(BASE_REPORT_DIR, PC_NAME)
os.makedirs(REPORT_DIR, exist_ok=True)

SYSTEM_LOG_TYPES = ["System", "Application"]
EVENT_TYPES = {
    win32con.EVENTLOG_ERROR_TYPE: "ERROR",
    win32con.EVENTLOG_WARNING_TYPE: "WARNING",
    win32con.EVENTLOG_INFORMATION_TYPE: "INFO"
}

def fetch_events(log_type: str, hours: int = 24):
    """Fetch Windows Event Logs of a specific type from the past X hours"""
    server = 'localhost'
    log_handle = win32evtlog.OpenEventLog(server, log_type)
    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
    time_threshold = datetime.datetime.now() - datetime.timedelta(hours=hours)

    events_summary = []
    while True:
        records = win32evtlog.ReadEventLog(log_handle, flags, 0)
        if not records:
            break
        for event in records:
            event_time = event.TimeGenerated.Format()
            event_dt = datetime.datetime.strptime(event_time, "%a %b %d %H:%M:%S %Y")
            if event_dt < time_threshold:
                return events_summary
            events_summary.append({
                "Type": EVENT_TYPES.get(event.EventType, "OTHER"),
                "Source": str(event.SourceName),
                "EventID": event.EventID & 0xFFFF,
                "Time": event_time,
                "Message": win32evtlogutil.SafeFormatMessage(event, log_type)[:200]  # Shorten message
            })
    return events_summary

def summarize_frequent_errors(events, label):
    """Count most common EventID+Source pairs"""
    error_keys = [f"{ev['EventID']}:{ev['Source']}" for ev in events if ev['Type'] == 'ERROR']
    counter = Counter(error_keys)
    top5 = counter.most_common(5)
    summary = f"\nTop 5 frequent ERRORs in the past {label}:\n"
    for k, v in top5:
        eid, src = k.split(":")
        summary += f"  {src} (Event ID {eid}): {v} times\n"
    return summary if top5 else f"\nNo frequent ERRORs found in the past {label}.\n"

def generate_report():
    now = datetime.datetime.now()
    filename = os.path.join(REPORT_DIR, f"System_Report_{PC_NAME}_{now.strftime('%Y-%m-%d')}.txt")
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"System Report for {PC_NAME} - {now.strftime('%A, %B %d, %Y')}\n")
        f.write("="*60 + "\n")
        for log in SYSTEM_LOG_TYPES:
            f.write(f"\n-- {log} Log --\n")
            events_24h = fetch_events(log, 24)
            events_7d = fetch_events(log, 24*7)
            events_30d = fetch_events(log, 24*30)

            if not events_24h:
                f.write("No recent critical events in the last 24 hours.\n")
            else:
                for ev in events_24h:
                    f.write(f"[{ev['Time']}] {ev['Type']} - {ev['Source']} (ID {ev['EventID']})\n")
                    f.write(f"    {ev['Message']}\n")

            f.write(summarize_frequent_errors(events_24h, "24 hours"))
            f.write(summarize_frequent_errors(events_7d, "7 days"))
            f.write(summarize_frequent_errors(events_30d, "30 days"))

    return filename

if __name__ == '__main__':
    path = generate_report()
    print(f"✅ Report saved to: {path}")
