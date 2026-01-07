import requests
from bs4 import BeautifulSoup
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import time
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

def get_fighter_info(url):
    url = f"{url}"
        
    try:
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print("Retry failed:", e)
        return {}
    
    soup = BeautifulSoup(response.text, "html.parser")

    stats = {
        "height": None,
        "weight": None,
        "reach": None,
        "stance": None,
        "dob": None,
        "slpm": None,
        "stracc": None,
        "sapm": None,
        "strdef": None,
        "tdavg": None,
        "tdacc": None,
        "tddef": None,
        "subavg": None
    }

    items = soup.select("li.b-list__box-list-item.b-list__box-list-item_type_block")

    for item in items:
        parts = item.text.strip().split(":")
        if len(parts) != 2:
            continue

        key = parts[0].strip().lower()
        value = parts[1].strip()

        if key == "height":
            stats["height"] = value
        elif key == "weight":
            stats["weight"] = value
        elif key == "reach":
            stats["reach"] = value
        elif key == "stance":
            stats["stance"] = value
        elif key == "dob":
            stats["dob"] = value
        elif key == "slpm":
            stats["slpm"] = value
        elif key == "str. acc.":
            stats["stracc"] = value
        elif key == "sapm":
            stats["sapm"] = value
        elif key == "str. def":
            stats["strdef"] = value
        elif key == "td avg.":
            stats["tdavg"] = value
        elif key == "td acc.":
            stats["tdacc"] = value
        elif key == "td def.":
            stats["tddef"] = value
        elif key == "sub. avg.":
            stats["subavg"] = value
            
    return stats

def main():
    with open("../web-app/data/fighterdata.json", "r", encoding="utf-8") as f:
        fighters = json.load(f)

    for fighter in fighters:
        url = fighter.get("url")

        if not url:
            continue

        stats = get_fighter_info(url)

        fighter.update(stats)

        time.sleep(1.5) 

    with open("../web-app/data/fighterdata_with_stats.json", "w", encoding="utf-8") as f:
        json.dump(fighters, f, indent=2)


if __name__ == "__main__":
    main()