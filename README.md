# SoupCalendar (starter)

Small service that scrapes STL soup kitchen / pantry hours and exposes calendar subscription feeds (ICS) for Apple/Google.

Features in this initial scaffold:
- Flask app serving .ics feeds for `soup_kitchen`, `food_pantry`, and `both`
- Scraper using Requests + BeautifulSoup
- Basic ICS generation using `ics` library with weekly RRULEs
- APScheduler job that updates cached ICS periodically
- Dockerfile + docker-compose for home server deployment

Next steps:
- Improve parser to handle more site variations
- Add Google OAuth flow (optional) to create calendars in users' accounts
- Add tests and CI

Run locally (dev):
1. python -m venv venv
2. source venv/bin/activate
3. pip install -r requirements.txt
4. FLASK_ENV=development FLASK_APP=src.app:app flask run

Run with Docker:
  docker-compose up --build
