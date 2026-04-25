import requests
from icalendar import Calendar
from datetime import datetime, date
import json
import os

AIRBNB_ICAL = os.environ.get('AIRBNB_ICAL_URL', '')
BOOKING_ICAL = os.environ.get('BOOKING_ICAL_URL', '')

def parse_ical(url, platform):
    if not url:
        print(f"HOIATUS: {platform} URL puudub!")
        return []
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        cal = Calendar.from_ical(resp.content)
        bookings = []
        for component in cal.walk():
            if component.name == "VEVENT":
                start = component.get('dtstart').dt
                end   = component.get('dtend').dt
                summary = str(component.get('summary', ''))

                if isinstance(start, datetime): start = start.date()
                if isinstance(end, datetime):   end   = end.date()

                # Booking.com saadab broneeritud päevad kui "CLOSED"
                if 'CLOSED' in summary.upper() or 'NOT AVAILABLE' in summary.upper():
                    guest = 'Broneeritud'
                elif summary.strip() == '':
                    guest = 'Broneering'
                else:
                    guest = summary.strip()

                bookings.append({
                    'start':    start.isoformat(),
                    'end':      end.isoformat(),
                    'guest':    guest,
                    'platform': platform
                })

        print(f"{platform}: leitud {len(bookings)} kirjet")
        return bookings

    except Exception as e:
        print(f"VIGA {platform}: {e}")
        return []


airbnb_bookings  = parse_ical(AIRBNB_ICAL,  'airbnb')
booking_bookings = parse_ical(BOOKING_ICAL, 'booking')

all_bookings = airbnb_bookings + booking_bookings
all_bookings.sort(key=lambda x: x['start'])

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump({
        'updated': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'bookings': all_bookings
    }, f, ensure_ascii=False, indent=2)

print(f"Kokku {len(all_bookings)} broneeringut salvestatud")
