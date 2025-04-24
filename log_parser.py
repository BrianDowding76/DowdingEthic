# log_parser.py
# Part of the DowdingEthic assistant system
# Description: Collects and summarizes critical Windows logs for daily reporting

import os
import datetime
import win32evtlog
import win32evtlogutil
import win32con

REPORT_DIR = os.path.expandvars(r"%USERPROFILE%\Documents\System Reports")
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

def generate_report():
    now = datetime.datetime.now()
    filename = os.path.join(REPORT_DIR, f"System_Report_{now.strftime('%Y-%m-%d')}.txt")
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"System Report for {now.strftime('%A, %B %d, %Y')}\n")
        f.write("="*60 + "\n")
        for log in SYSTEM_LOG_TYPES:
            f.write(f"\n-- {log} Log --\n")
            events = fetch_events(log)
            if not events:
                f.write("No recent critical events.\n")
            for ev in events:
                f.write(f"[{ev['Time']}] {ev['Type']} - {ev['Source']} (ID {ev['EventID']})\n")
                f.write(f"    {ev['Message']}\n")
    return filename

if __name__ == '__main__':
    path = generate_report()
    print(f"✅ Report saved to: {path}")

