import requests
from bs4 import BeautifulSoup
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

session = requests.Session()

retry_strategy = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)

adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)


def get_fighter_win_streak(fighter_url: str):
    try:
        r = session.get(fighter_url, headers=headers, timeout=10)
        r.raise_for_status()
    except:
        return {"cur_streak": 0, "max_streak": 0}
        print("Retry failed:", e)

    soup = BeautifulSoup(r.text, "html.parser")

    rows = soup.select("table.b-fight-details__table tbody tr")

    results = []
    for r in rows:
        res = r.select_one("td.b-fight-details__table-col:nth-of-type(1) p")
        if res:
            results.append(res.text.strip().upper())

    cur = 0
    maxs = 0
    for r in results:
        if r == "WIN":
            cur += 1
        else:
            cur = 0
        maxs = max(maxs, cur)
    
    return {
        "cur_streak": cur,
        "max_streak": maxs,
    }
    
def main():
    with open("../web-app/data/fighterdata_with_stats.json", "r", encoding="utf-8") as f:
        fighters = json.load(f)

    for fighter in fighters:
        url = fighter.get("url")
        if not url:
            print("NO URL FOUND")
            continue

        streaks = get_fighter_win_streak(url)
        fighter.update(streaks)

    with open("../web-app/data/fighterdata_with_stats.json", "w", encoding="utf-8") as f:
        json.dump(fighters, f, indent=4)
        
if __name__ == "__main__":
    main()