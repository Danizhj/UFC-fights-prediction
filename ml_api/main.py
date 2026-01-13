from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pickle
import json
import pandas as pd
import numpy as np

with open("./model.pkl", "rb") as f:
    model = pickle.load(f)

with open("./processed_fighterdata.json", "r", encoding="utf-8") as f:
    FIGHTERS = json.load(f)

FIGHTER_INDEX = {f["name"]: f for f in FIGHTERS}

class PredictRequest(BaseModel):
    fighter1: str
    fighter2: str

def get_fighter(name: str):
    fighter = FIGHTER_INDEX.get(name)
    if not fighter:
        raise HTTPException(status_code=400, detail=f"Fighter not found: {name}")
    
    for key in ["height", "reach", "age", "slpm", "sapm", "stracc", "strdef",
                "tdavg", "tdacc", "tddef", "subavg", "max_streak", "cur_streak", "stance"]:
        if key not in fighter:
            fighter[key] = 0  
    return fighter

app = FastAPI()

FEATURE_ORDER = [
    "height_diff", "reach_diff", "stance_matchup", "age_diff",
    "slpm_diff", "stracc_diff", "sapm_diff", "strdef_diff",
    "tdavg_diff", "tdacc_diff", "tddef_diff",
    "subavg_diff","max_streak_diff", "cur_streak_diff"
]

def build_features(f1, f2):
    return {
        "height_diff": f1["height"] - f2["height"],
        "reach_diff": f1["reach"] - f2["reach"],
        "stance_matchup": int(str(f1['stance']) + str(f2['stance'])),
        "age_diff": f1["age"] - f2["age"],
        "slpm_diff": f1["slpm"] - f2["slpm"],
        "sapm_diff": f1["sapm"] - f2["sapm"],
        "stracc_diff": f1["stracc"] - f2["stracc"],
        "strdef_diff": f1["strdef"] - f2["strdef"],
        "tdavg_diff": f1["tdavg"] - f2["tdavg"],
        "tdacc_diff": f1["tdacc"] - f2["tdacc"],
        "tddef_diff": f1["tddef"] - f2["tddef"],
        "subavg_diff": f1["subavg"] - f2["subavg"],
        "max_streak_diff": f1["max_streak"] - f2["max_streak"],
        "cur_streak_diff": f1["cur_streak"] - f2["cur_streak"],
    }
    
@app.post("/predict")
def predict(req: PredictRequest):
    f1 = get_fighter(req.fighter1)

    f2 = get_fighter(req.fighter2)

    X = build_features(f1, f2)

    X_array = np.array([X[f] for f in FEATURE_ORDER]).reshape(1, -1)

    pred = model.predict(X_array)[0]
    
    proba = model.predict_proba(X_array)[0]

    return {
        "winner": req.fighter1 if pred == 1 else req.fighter2,
        "looser": req.fighter2 if pred == 1 else req.fighter1,
        "confidence": float(max(proba))
    }