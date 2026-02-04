from flask import Flask, Response, render_template_string, url_for
from .scraper import fetch_page, parse_locations
from .ics_generator import make_calendar_for_locations
from .config import TIMEZONE, CACHE_DIR
from apscheduler.schedulers.background import BackgroundScheduler
import os

app = Flask(__name__)

# simple in-memory cache
_cached = {}

INDEX_HTML = """
<!doctype html>
<title>SoupCalendar</title>
<h1>Soup & Pantry Calendar Subscriptions</h1>
<ul>
  <li><a href="/calendars/soup_kitchen.ics">Subscribe: Soup Kitchen (ICS)</a></li>
  <li><a href="/calendars/food_pantry.ics">Subscribe: Food Pantry (ICS)</a></li>
  <li><a href="/calendars/both.ics">Subscribe: Both (ICS)</a></li>
</ul>
<p>To subscribe in Google Calendar: <em>Settings &gt; Add calendar &gt; From URL</em> and paste one of the .ics URLs above.</p>
"""


@app.route('/')
def index():
    return render_template_string(INDEX_HTML)


@app.route('/calendars/<name>.ics')
def calendar_feed(name):
    # name in ['soup_kitchen','food_pantry','both']
    cal_text = _cached.get(name)
    if not cal_text:
        return Response('Not ready yet', status=503)
    return Response(cal_text, mimetype='text/calendar')


def generate_and_cache():
    html = fetch_page()
    locs = parse_locations(html)
    # very simple split: items with 'soup' or 'kitchen' in name -> soup_kitchen, 'pantry' -> food_pantry
    soup_locs = [l for l in locs if 'soup' in l['name'].lower() or 'kitchen' in l['name'].lower()]
    pantry_locs = [l for l in locs if 'pantry' in l['name'].lower() or 'food pantry' in l['notes'].lower()]
    both = list({id(l): l for l in (soup_locs + pantry_locs)}.values())

    c_soup = make_calendar_for_locations(soup_locs, tz_name=TIMEZONE)
    c_pantry = make_calendar_for_locations(pantry_locs, tz_name=TIMEZONE)
    c_both = make_calendar_for_locations(both, tz_name=TIMEZONE)

    _cached['soup_kitchen'] = c_soup.serialize()
    _cached['food_pantry'] = c_pantry.serialize()
    _cached['both'] = c_both.serialize()


def start_scheduler():
    scheduler = BackgroundScheduler()
    # run at startup and then periodically
    generate_and_cache()
    scheduler.add_job(generate_and_cache, 'interval', minutes=int(os.getenv('UPDATE_INTERVAL_MINUTES', 1440)))
    scheduler.start()


start_scheduler()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
