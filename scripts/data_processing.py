import pandas as pd
from sklearn.model_selection import train_test_split
import json

def height_processing(fighters):
    for fighter in fighters:
        h = fighter.get('height')
        h = h.replace('"', '')
        feet, inches = h.split("'")
        feet = int(feet.strip())
        inches = int(inches.strip())
        
        total_inches = feet * 12 + inches
        
        fighter['height'] = total_inches
            
    return fighters

def reach_processing(fighters):
    for fighter in fighters:
        r = fighter.get('reach')
        r = r.replace('"', '')
        fighter['reach'] = int(r)
    
    return fighters    
    
def age_processing(fighters):
    for fighter in fighters:
        dob = fighter.get('dob')
                
        month, year = dob.split(",")
        
        cur_year = 2025
        
        age = cur_year - int(year)
        fighter['age'] = age

    return fighters
        
def career_stats_processing(fighters):
    cs = ['stracc', 'strdef', 'tdacc', 'tddef']
    csint = ['slpm', 'sapm', 'tdavg', 'subavg']
    
    for fighter in fighters:
        for stat in cs:
            s = fighter.get(stat)
            
            s = s.replace('%', '')
            s = int(s) / 100
            
            fighter[stat] = s
        for stat in csint:
            s = fighter.get(stat)
            fighter[stat] = float(s)
    
    return fighters
        
def stance_processing(fighters):
    encoding_dict = {
        'Southpaw': 0,
        'Switch': 1,
        'Orthodox': 2,
        'Open Stance': 3
    }
    for fighter in fighters:
        stance = fighter.get("stance")
        fighter['stance'] = encoding_dict.get(stance)
    return fighters

def data_preprocessing(fighters):
    fighters = height_processing(fighters)
    fighters = reach_processing(fighters)
    fighters = age_processing(fighters)
    fighters = career_stats_processing(fighters)
    fighters = stance_processing(fighters)
    for fighter in fighters:
        del fighter['dob']
        del fighter['weight']
    return fighters
    
def main():
    with open("../web-app/data/fighterdata_with_stats.json", "r", encoding="utf-8") as f:
        fighters = json.load(f)
    fighters = data_preprocessing(fighters)
    with open("../web-app/data/processed_fighterdata.json", "w", encoding="utf-8") as f:
        json.dump(fighters, f, indent=4)
        
if __name__ == "__main__":
    main()