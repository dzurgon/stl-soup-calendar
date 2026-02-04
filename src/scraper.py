import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import re
from .config import SCRAPE_URL, USER_AGENT

Session = requests.Session()
Session.headers.update({"User-Agent": USER_AGENT})


def fetch_page(url: str = SCRAPE_URL) -> str:
    r = Session.get(url, timeout=20)
    r.raise_for_status()
    return r.text


def parse_locations(html: str) -> List[Dict[str, Any]]:
    """Parse the Star the Rest STL page and return list of locations.

    Each item: {"name": str, "address": str, "hours": [str], "notes": str}
    """
    soup = BeautifulSoup(html, "html.parser")
    results = []

    # Heuristic parsing: look for content in sections under "Food Programs & Pantries"
    # The page structure may vary; this tries to be resilient.
    main = soup.find(id=re.compile("food|pantri", re.I)) or soup

    # find blocks that look like locations: headings followed by paragraphs/lists
    for heading in main.find_all(re.compile('h2|h3|h4')):
        title = heading.get_text(strip=True)
        # skip generic headings
        if len(title) < 3:
            continue
        # gather following siblings until next heading
        content = []
        for sib in heading.find_next_siblings():
            if sib.name and re.match(r'h[1-6]', sib.name):
                break
            content.append(sib)
        if not content:
            continue
        text = "\n".join(c.get_text(separator=" \n", strip=True) for c in content)
        # simple heuristics for address and hours
        address = ""
        hours = []
        notes = ""

        # try to extract address lines: presence of numbers and street abbreviations
        addr_match = re.search(r"\d{1,5} [\w\s.#,-]+", text)
        if addr_match:
            address = addr_match.group(0)

        # find lines that look like hours: contain days or time ranges (am/pm or :)
        for line in text.splitlines():
            if re.search(r"\b(Mon|Tue|Wed|Thu|Fri|Sat|Sun|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b", line, re.I) or re.search(r"\d{1,2}:\d{2}", line):
                hours.append(line.strip())
        # the rest as notes
        notes = "\n".join([l for l in text.splitlines() if l.strip() and l.strip() not in hours])

        results.append({"name": title, "address": address, "hours": hours, "notes": notes})

    return results


if __name__ == "__main__":
    html = fetch_page()
    locs = parse_locations(html)
    import json
    print(json.dumps(locs, indent=2))
