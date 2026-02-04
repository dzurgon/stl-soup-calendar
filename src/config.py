import os
from dotenv import load_dotenv
load_dotenv()

SCRAPE_URL = os.getenv("SCRAPE_URL", "https://www.startherestl.org/food-programs--pantries.html")
TIMEZONE = os.getenv("TIMEZONE", "America/Chicago")
CACHE_DIR = os.getenv("CACHE_DIR", "/data")
UPDATE_INTERVAL_MINUTES = int(os.getenv("UPDATE_INTERVAL_MINUTES", "1440"))
USER_AGENT = os.getenv("USER_AGENT", "SoupCalendarBot/0.1 (+https://pustl.com)")
