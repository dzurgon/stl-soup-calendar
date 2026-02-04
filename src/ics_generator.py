from ics import Calendar, Event
from datetime import datetime, timedelta, time
from dateutil import rrule, parser as dateparser
import pytz
import re
from typing import List, Dict, Any

WEEKDAY_MAP = {
    'monday': 'MO', 'mon': 'MO',
    'tuesday': 'TU', 'tue': 'TU', 'tues': 'TU',
    'wednesday': 'WE', 'wed': 'WE',
    'thursday': 'TH', 'thu': 'TH', 'thur': 'TH',
    'friday': 'FR', 'fri': 'FR',
    'saturday': 'SA', 'sat': 'SA',
    'sunday': 'SU', 'sun': 'SU'
}


def parse_time_range(text: str):
    """Return (start_time, end_time) as time objects if found, else None."""
    # look for patterns like 12:00 PM - 2:00 PM
    m = re.search(r"(\d{1,2}:?\d{0,2}\s*[ap]\.?m\.?)\s*-\s*(\d{1,2}:?\d{0,2}\s*[ap]\.?m\.?)", text, re.I)
    if m:
        try:
            t0 = dateparser.parse(m.group(1)).time()
            t1 = dateparser.parse(m.group(2)).time()
            return t0, t1
        except Exception:
            return None
    return None


def parse_days(text: str) -> List[str]:
    """Return list of weekday codes like ['MO','TU'] found in text."""
    found = []
    text = text.lower()
    for k in WEEKDAY_MAP:
        if re.search(r"\b" + re.escape(k) + r"\b", text):
            found.append(WEEKDAY_MAP[k])
    return sorted(set(found), key=lambda x: ['MO','TU','WE','TH','FR','SA','SU'].index(x))


def next_weekday_occurrence(weekday_code: str, tz):
    # return a datetime for next occurrence of the weekday starting at today
    today = datetime.now(tz).date()
    weekday_index = {'MO':0,'TU':1,'WE':2,'TH':3,'FR':4,'SA':5,'SU':6}[weekday_code]
    days_ahead = (weekday_index - today.weekday() + 7) % 7
    return today + timedelta(days=days_ahead)


def make_calendar_for_locations(locations: List[Dict[str, Any]], tz_name: str = 'America/Chicago') -> Calendar:
    cal = Calendar()
    tz = pytz.timezone(tz_name)
    for loc in locations:
        name = loc.get('name')
        address = loc.get('address', '')
        notes = loc.get('notes', '')
        for hline in loc.get('hours', []):
            days = parse_days(hline)
            tr = parse_time_range(hline)
            if not days or not tr:
                # skip lines we cannot parse for now
                continue
            start_t, end_t = tr
            # create an event per day pattern with RRULE weekly
            rrule_byday = ",".join(days)
            # for DTSTART pick next occurrence of first day
            first_day = days[0]
            dt_date = next_weekday_occurrence(first_day, tz)
            dtstart = datetime.combine(dt_date, start_t)
            dtend = datetime.combine(dt_date, end_t)
            dtstart = tz.localize(dtstart)
            dtend = tz.localize(dtend)

            ev = Event()
            ev.name = f"{name} - {hline}"
            ev.begin = dtstart
            ev.end = dtend
            ev.make_all_day(False)
            ev.location = address
            ev.description = notes
            # add RRULE via extra property (ics lib supports it)
            ev.extra.append(('RRULE', f'FREQ=WEEKLY;BYDAY={rrule_byday}'))
            cal.events.add(ev)
    return cal


if __name__ == '__main__':
    # quick smoke test
    sample = [{'name':'Test Pantry','address':'123 Main St','hours':['Tuesdays 12:00 PM - 2:00 PM','Wed 9:00 AM - 11:00 AM'],'notes':'Notes here'}]
    c = make_calendar_for_locations(sample)
    print(c)
