import requests
from icalendar import Calendar
from datetime import datetime, date
import json
import os

# URL-id tulevad GitHub Secrets'ist
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
                summary = str(component.get('summary', 'Broneering'))

                # Normaliseeri kuupäevaks
                if isinstance(start, datetime):
                    start = start.date()
                if isinstance(end, datetime):
                    end = end.date()

                # Airbnb lisab mõnikord "Not available" blocked päevad — jäta alles
                bookings.append({
                    'start':    start.isoformat(),
                    'end':      end.isoformat(),
                    'guest':    summary,
                    'platform': platform
                })

        print(f"{platform}: leitud {len(bookings)} kirjet")
        return bookings

    except Exception as e:
        print(f"VIGA {platform}: {e}")
        return []


# Loe mõlemad
airbnb_bookings  = parse_ical(AIRBNB_ICAL,  'airbnb')
booking_bookings = parse_ical(BOOKING_ICAL, 'booking')

all_bookings = airbnb_bookings + booking_bookings
all_bookings.sort(key=lambda x: x['start'])

# Salvesta
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump({
        'updated': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'bookings': all_bookings
    }, f, ensure_ascii=False, indent=2)

print(f"Kokku {len(all_bookings)} broneeringut salvestatud data.json-i")
