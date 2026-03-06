from __future__ import annotations

import json
import os
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlencode, quote
from urllib.request import urlopen


def iso_utc(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_datetime(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    dt = datetime.fromisoformat(normalized)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def parse_event_range(event: Dict) -> Optional[Tuple[date, date, Dict]]:
    start = event.get("start", {})
    end = event.get("end", {})

    if "date" in start and "date" in end:
        start_day = date.fromisoformat(start["date"])
        end_exclusive = date.fromisoformat(end["date"])
        if end_exclusive <= start_day:
            end_exclusive = start_day + timedelta(days=1)
        duration = max(1, (end_exclusive - start_day).days)
        info = {
            "summary": event.get("summary") or "Evento",
            "allDay": True,
            "durationDays": duration,
        }
        return start_day, end_exclusive, info

    if "dateTime" in start and "dateTime" in end:
        start_dt = parse_datetime(start["dateTime"])
        end_dt = parse_datetime(end["dateTime"])

        start_day = start_dt.date()
        end_exclusive = end_dt.date()

        if end_dt.time() != time(0, 0):
            end_exclusive += timedelta(days=1)
        if end_exclusive <= start_day:
            end_exclusive = start_day + timedelta(days=1)

        duration = max(1, (end_exclusive - start_day).days)
        info = {
            "summary": event.get("summary") or "Evento",
            "allDay": False,
            "durationDays": duration,
        }
        return start_day, end_exclusive, info

    return None


def fetch_events(calendar_id: str, api_key: str, time_min: str, time_max: str) -> List[Dict]:
    base = f"https://www.googleapis.com/calendar/v3/calendars/{quote(calendar_id, safe='')}/events"
    events: List[Dict] = []
    page_token: Optional[str] = None

    while True:
        params = {
            "key": api_key,
            "singleEvents": "true",
            "orderBy": "startTime",
            "maxResults": "2500",
            "timeMin": time_min,
            "timeMax": time_max,
        }
        if page_token:
            params["pageToken"] = page_token

        url = f"{base}?{urlencode(params)}"
        with urlopen(url) as response:
            payload = json.loads(response.read().decode("utf-8"))

        items = payload.get("items") or []
        events.extend(items)

        page_token = payload.get("nextPageToken")
        if not page_token:
            break

    return events


def main() -> int:
    api_key = os.getenv("GOOGLE_CALENDAR_API_KEY", "").strip()
    calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "").strip()

    if not api_key or not calendar_id:
        print("Skipping update: missing GOOGLE_CALENDAR_API_KEY or GOOGLE_CALENDAR_ID")
        return 0

    today = datetime.now(timezone.utc).date()
    range_start = datetime.combine(today - timedelta(days=365), time.min, tzinfo=timezone.utc)
    range_end = datetime.combine(today + timedelta(days=730), time.min, tzinfo=timezone.utc)

    events = fetch_events(calendar_id, api_key, iso_utc(range_start), iso_utc(range_end))

    blocked_dates = set()
    events_by_date: Dict[str, List[Dict]] = {}

    for event in events:
        if event.get("status") == "cancelled":
            continue

        parsed = parse_event_range(event)
        if not parsed:
            continue

        start_day, end_exclusive, event_info = parsed
        day = start_day
        while day < end_exclusive:
            date_str = day.isoformat()
            blocked_dates.add(date_str)
            events_by_date.setdefault(date_str, []).append(event_info)
            day += timedelta(days=1)

    sorted_dates = sorted(blocked_dates)
    sorted_events_by_date = {key: events_by_date[key] for key in sorted(events_by_date.keys())}

    payload = {
        "updatedAt": iso_utc(datetime.now(timezone.utc)),
        "blockedDates": sorted_dates,
        "eventsByDate": sorted_events_by_date,
    }

    output_path = Path(__file__).resolve().parents[1] / "availability.json"
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote {len(sorted_dates)} blocked dates to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
