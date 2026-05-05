from __future__ import annotations

import json
import os
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, quote
from urllib.request import urlopen
from zoneinfo import ZoneInfo


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


def fetch_events(
    calendar_id: str,
    api_key: str,
    time_min: str,
    time_max: str,
    calendar_time_zone: str,
) -> List[Dict]:
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
            "timeZone": calendar_time_zone,
        }
        if page_token:
            params["pageToken"] = page_token

        url = f"{base}?{urlencode(params)}"
        try:
            with urlopen(url) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"Google Calendar API HTTP {exc.code}. Response: {details}"
            ) from exc
        except URLError as exc:
            raise RuntimeError(f"Google Calendar API network error: {exc.reason}") from exc

        items = payload.get("items") or []
        events.extend(items)

        page_token = payload.get("nextPageToken")
        if not page_token:
            break

    return events


def write_outputs(project_root: Path, payload: Dict, public_calendar_config: Optional[Dict] = None) -> None:
    output_path = project_root / "availability.json"
    output_js_path = project_root / "availability.js"

    json_payload = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    js_chunks = [
        f"window.__ESTANCIA_AVAILABILITY__ = {json.dumps(payload, ensure_ascii=False, indent=2)};",
    ]

    if public_calendar_config:
        js_chunks.append(
            f"window.__ESTANCIA_CALENDAR_CONFIG__ = {json.dumps(public_calendar_config, ensure_ascii=False, indent=2)};"
        )

    js_payload = "\n".join(js_chunks) + "\n"

    output_path.write_text(json_payload, encoding="utf-8")
    output_js_path.write_text(js_payload, encoding="utf-8")


def main() -> int:
    api_key = os.getenv("GOOGLE_CALENDAR_API_KEY", "").strip()
    calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "").strip()
    calendar_time_zone_name = os.getenv("GOOGLE_CALENDAR_TIMEZONE", "America/Sao_Paulo").strip() or "America/Sao_Paulo"
    project_root = Path(__file__).resolve().parents[1]

    if not api_key or not calendar_id:
        existing_json = project_root / "availability.json"
        if existing_json.exists():
            payload = json.loads(existing_json.read_text(encoding="utf-8"))
            write_outputs(project_root, payload)
            print("Skipping remote update: missing GOOGLE_CALENDAR_API_KEY or GOOGLE_CALENDAR_ID")
            print("Regenerated availability.js from existing availability.json")
            return 0

        print("Skipping update: missing GOOGLE_CALENDAR_API_KEY or GOOGLE_CALENDAR_ID")
        return 0

    try:
        calendar_time_zone = ZoneInfo(calendar_time_zone_name)
    except Exception:
        calendar_time_zone_name = "America/Sao_Paulo"
        calendar_time_zone = ZoneInfo(calendar_time_zone_name)

    today = datetime.now(calendar_time_zone).date()
    range_start = datetime.combine(today - timedelta(days=365), time.min, tzinfo=calendar_time_zone)
    range_end = datetime.combine(today + timedelta(days=730), time.min, tzinfo=calendar_time_zone)

    events = fetch_events(
        calendar_id,
        api_key,
        iso_utc(range_start),
        iso_utc(range_end),
        calendar_time_zone_name,
    )

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
        "updatedAtLocal": datetime.now(calendar_time_zone).replace(microsecond=0).isoformat(),
        "source": "availability-snapshot",
        "sourceTimeZone": calendar_time_zone_name,
        "blockedDates": sorted_dates,
        "eventsByDate": sorted_events_by_date,
    }

    public_calendar_config = {
        "apiKey": api_key,
        "calendarId": calendar_id,
        "timeZone": calendar_time_zone_name,
    }

    write_outputs(project_root, payload, public_calendar_config)

    output_path = project_root / "availability.json"
    output_js_path = project_root / "availability.js"
    print(f"Wrote {len(sorted_dates)} blocked dates to {output_path}")
    print(f"Wrote availability snapshot to {output_js_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
