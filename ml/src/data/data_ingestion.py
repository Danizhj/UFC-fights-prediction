import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import random
import time
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import logging
from sklearn.model_selection import train_test_split

# Logging configuration
logger = logging.getLogger('data_ingestion')
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('errors.log')
file_handler.setLevel(logging.ERROR)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)


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

def get_events():
    events = []
    try:
        url = "http://www.ufcstats.com/statistics/events/completed?page=all"
        html = requests.get(url, headers=headers).text
        soup = BeautifulSoup(html, "html.parser")
        
        rows = soup.select("table.b-statistics__table-events tbody tr")

        for r in rows:
            link = r.select_one("td:nth-of-type(1) a")
            date = r.select_one("td:nth-of-type(1) span")
            if not link or not date:
                continue

            event_name = link.text.strip()
            event_url = link['href']
            event_date = int(date.text.strip().split(",")[1])

            events.append({
                "event_name": event_name,
                "event_url": event_url,
                "event_date": event_date
            })
        del events[0]
        
        logger.debug("Successfully loaded events")
    except Exception as e:
        logger.error("Failed to load events %s", e)
    return events

def get_fights(event):
    url = event['event_url']
    html = requests.get(url, headers=headers).text
    soup = BeautifulSoup(html, 'html.parser')
    
    fights = []
    
    rows = soup.select("table.b-fight-details__table tbody tr")
    
    for r in rows:
        winner = r.select_one("td:nth-of-type(2) p:nth-of-type(1) a").text.strip()
        looser = r.select_one("td:nth-of-type(2) p:nth-of-type(2) a").text.strip()
        fighter1_url = r.select_one("td:nth-of-type(2) p:nth-of-type(1) a")['href']
        fighter2_url = r.select_one("td:nth-of-type(2) p:nth-of-type(2) a")['href']
        
        fights.append({
            "winner": winner,
            "winner_url": fighter1_url,
            "looser": looser,
            "looser_url": fighter2_url,
            "fight_date": event['event_date']
        })
    return fights

def get_win_streaks(fighter1_url, opponent_name):
    try:
        r = session.get(fighter1_url, headers=headers, timeout=10)
        r.raise_for_status()
    except:
        return {"cur_streak": 0, "max_streak": 0}

    soup = BeautifulSoup(r.text, "html.parser")

    name = soup.select_one("span.b-content__title-highlight").text.strip()

    rows = soup.select("table.b-fight-details__table tbody tr")

    fight_idx = None
    for idx, row in enumerate(rows):
        names = row.select("td.b-fight-details__table-col:nth-of-type(2) a")
        if len(names) < 2:
            continue

        p1, p2 = names[0].text.strip(), names[1].text.strip()

        if {p1, p2} == {name, opponent_name}:
            fight_idx = idx
            break

    if fight_idx is None:
        return {"cur_streak": 0, "max_streak": 0}

    last_fights = rows[fight_idx + 1:]
    last_fights = last_fights[::-1]

    results = []
    for r in last_fights:
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
    
def get_fights_ds():
    try:
        events = get_events()
        all_fights = [get_fights(event) for event in events]
        all_fights = [fight for event in all_fights for fight in event]
        
        fights_dataset = pd.DataFrame(all_fights)
        
        for idx, fight in fights_dataset.iterrows():
            random_state = random.randint(0, 1)
        
            if random_state == 1:
                fights_dataset.at[idx, 'outcome'] = 1
            else:
                fights_dataset.at[idx, 'outcome'] = 0
                
                winner_temp = fight['winner']
                looser_temp = fight['looser']
                winner_url_temp = fight['winner_url']
                looser_url_temp = fight['looser_url']
                
                fights_dataset.at[idx, 'winner'] = looser_temp
                fights_dataset.at[idx, 'winner_url'] = looser_url_temp
                fights_dataset.at[idx, 'looser'] = winner_temp
                fights_dataset.at[idx, 'looser_url'] = winner_url_temp

        logger.debug("Successfully loaded fights dataset")
    except Exception as e:
        logger.error('Failed to get fights dataset %s', e)
        
    return fights_dataset

def get_fights_ds_with_stats(fights_dataset):
    fighter_cache = {}
    
    try:
        for idx, fight in fights_dataset.iterrows():
            url_1 = fights_dataset.at[idx, 'winner_url']
            url_2 = fights_dataset.at[idx, 'looser_url']
            
            if url_1 not in fighter_cache:
                fighter_cache[url_1] = get_fighter_info(url_1)
                fighter_1_stats = fighter_cache[url_1]
                time.sleep(random.uniform(1.0, 2.5))
            else:
                fighter_1_stats = fighter_cache[url_1]

            if url_2 not in fighter_cache:
                fighter_cache[url_2] = get_fighter_info(url_2)
                fighter_2_stats = fighter_cache[url_2]
                time.sleep(random.uniform(1.0, 2.5))
            else:
                fighter_2_stats = fighter_cache[url_2]
            
            for item in fighter_1_stats:
                fights_dataset.at[idx, item + "_1"] = fighter_1_stats[item]
                
            for item in fighter_2_stats:
                fights_dataset.at[idx, item + "_2"] = fighter_2_stats[item]
                
            if idx % 500 == 0:
                fights_dataset.to_csv("../../data/raw/progress.csv", index=False)
        
        logger.debug("Successfully loaded fighters' stats")
    except Exception as e:
        logger.error("Failed to load fighters' stats, %s", e)
    # get win streaks
    
    fighter_cache = {}
    ws_df = pd.DataFrame()
    
    try:
        for idx, fight in fights_dataset.iterrows():
            url_1 = fights_dataset.at[idx, 'winner_url']
            url_2 = fights_dataset.at[idx, 'looser_url']
            opp_name_1 = fights_dataset.at[idx, 'looser']
            opp_name_2 = fights_dataset.at[idx, 'winner']
            
            if url_1 not in fighter_cache:
                fighter_cache[url_1] = get_win_streaks(url_1, opp_name_1)
                fighter_1_stats = fighter_cache[url_1]
                time.sleep(random.uniform(1.0, 2.5))
            else:
                fighter_1_stats = fighter_cache[url_1]
                
            if url_2 not in fighter_cache:
                    fighter_cache[url_2] = get_win_streaks(url_2, opp_name_2)
                    fighter_2_stats = fighter_cache[url_2]
                    time.sleep(random.uniform(1.0, 2.5))
            else:
                fighter_2_stats = fighter_cache[url_2]
            
            for item in fighter_1_stats:
                ws_df.at[idx, item + "_1"] = fighter_1_stats[item]
                
            for item in fighter_2_stats:
                ws_df.at[idx, item + "_2"] = fighter_2_stats[item]
                
            if idx % 500 == 0:
                ws_df.to_csv("../../data/raw/progress_ws2.csv", index=False)
        
        logger.debug("Successfully loaded fighters' win streaks")
    except Exception as e:
        logger.error("Failed to load fighters' win streaks %s", e)
    # concat 2 dataframes
    
    fights_dataset = pd.concat([fights_dataset, ws_df], axis=1)
    
    fights_dataset = fights_dataset.drop(['winner_url', 'looser_url'], axis=1)
    
    return fights_dataset

def save_data(dataset: pd.DataFrame):
    try:
        dataset.to_csv("../../data/raw/fights_dataset_with_stats.csv", index=False)
        
        test, train = train_test_split(dataset, test_size=0.7, random_state=123, shuffle=False)
        train.to_csv("../../data/raw/train_raw.csv", index=False)
        test.to_csv("../../data/raw/test_raw.csv", index=False)
        
        data_path = os.path.abspath('../../data/raw')
        
        logger.debug('Data saved in %s', data_path)
    except Exception as e:
        logger.error('Error occured during saving the data %s', e)

def main():
    fights_dataset = get_fights_ds()
    
    fights_dataset_with_stats = get_fights_ds_with_stats(fights_dataset)
    
    save_data(fights_dataset_with_stats)
    
if __name__ == "__main__":
    main()