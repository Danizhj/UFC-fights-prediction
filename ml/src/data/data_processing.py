import pandas as pd
import logging
from sklearn.model_selection import train_test_split
import os

# Logging configuration
logger = logging.getLogger('data_processing')
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

def drop_nas(df: pd.DataFrame):
    df = df.dropna()
    df = df.drop_duplicates()
    df = df[~((df.slpm_1 == 0.0) | (df.slpm_2 == 0.0))]
    df = df[~((df.reach_1 == "--") | (df.reach_2 == "--"))]
    df = df[~((df.height_1 == "--") | (df.height_2 == "--"))]
    df = df[~((df.dob_1 == "--") | (df.dob_2 == "--"))]
    return df

def height_processing(df: pd.DataFrame):
    try:
        for idx, row in df.iterrows():
            for col in ['height_1', 'height_2']:
                h = row[col]
                
                h = h.replace('"', '')

                feet, inches = h.split("'")
                feet = int(feet.strip())
                inches = int(inches.strip())
                
                total_inches = feet * 12 + inches
                
                df.at[idx, col] = total_inches
                
        logger.debug("Height preprocessed")
        return df
    except Exception as e:
        logger.error("Failed to preprocess height %s", e)
        raise
    
def weight_processing(df: pd.DataFrame):
    try:
        df = df.drop('weight_2', axis=1)
        df.rename(columns={"weight_1": "weight"}, inplace=True)

        for idx, row in df.iterrows():
            w = row['weight']
            w = w.strip()
            w = w.replace('lbs.', '')
            
            df.at[idx, 'weight'] = int(w)
        
        logger.debug("Weight preprocessed")
        return df
    except Exception as e:
        logger.error("Failed to preprocess weight %s", e)
        raise

def reach_processing(df: pd.DataFrame):
    try:
        for idx, row in df.iterrows():
            for col in ['reach_1', 'reach_2']:
                r = row[col]
                
                r = r.replace('"', '')

                df.at[idx, col] = int(r)
                
        logger.debug("Reach processed")
        return df
    except Exception as e:
        logger.error("Failed to preprocess reach %s", e)
        raise
    
def age_processing(df: pd.DataFrame):
    try:
        for idx, row in df.iterrows():
            for col in ['dob_1', 'dob_2']:
                dob = row[col]
                
                month, year = dob.split(",")
                
                fight_date = df.at[idx, 'fight_date']
                
                age = fight_date - int(year)
                
                df.at[idx, col] = age

        df = df.rename(columns={'dob_1': 'age_1', 'dob_2': 'age_2'})
        df = df.drop('fight_date', axis=1)
        
        logger.debug("Age preprocessed")
        return df
    except Exception as e:
        logger.error("Failed to preprocess age %s", e)
        raise
        
def career_stats_processing(df: pd.DataFrame):
    try:
        cs_cols = ['stracc_1', 'strdef_1', 'tdacc_1', 'tddef_1', 'stracc_2', 'strdef_2', 'tdacc_2', 'tddef_2']

        for idx, row in df.iterrows():
            for col in cs_cols:
                s = row[col]
                
                s = s.replace('%', '')
                s = int(s) / 100
                
                df.at[idx, col] = s
        
        logger.debug("Career stats preprocessed")
        return df
    except Exception as e:
        logger.error("Failed to preprocess career stats %s", e)
        raise
        
def stance_processing(df: pd.DataFrame):
    try:
        encoding_dict = {
            'Southpaw': 0,
            'Switch': 1,
            'Orthodox': 2,
            'Open Stance': 3
        }

        df.stance_1 = df.stance_1.map(encoding_dict)
        df.stance_2 = df.stance_2.map(encoding_dict)
        
        logger.debug("Stance preprocessed")
        return df
    except Exception as e:
        logger.error("Failed to preprocess stance %s", e)
        raise
    
def data_preprocessing(df: pd.DataFrame):
    df = height_processing(df)
    df = weight_processing(df)
    df = reach_processing(df)
    df = age_processing(df)
    df = career_stats_processing(df)
    df = stance_processing(df)
    
    df = df.drop(['winner', 'looser'], axis=1)
    return df
    
def feature_engineering(df: pd.DataFrame):
    try:
        drop_cols = df.columns[:-1]

        for idx, row in df.iterrows():
            
            height_1 = df.at[idx, 'height_1']
            height_2 = df.at[idx, 'height_2']
            df.at[idx, 'height_diff'] = height_1 - height_2
            
            reach_1 = df.at[idx, 'reach_1']
            reach_2 = df.at[idx, 'reach_2']
            df.at[idx, 'reach_diff'] = reach_1 - reach_2
            
            stance_1 = df.at[idx, 'stance_1']
            stance_2 = df.at[idx, 'stance_2']
            df.at[idx, 'stance_matchup'] = int(str(stance_1) + str(stance_2))
            
            age_1 = df.at[idx, 'age_1']
            age_2 = df.at[idx, 'age_2']
            df.at[idx, 'age_diff'] = age_1 - age_2
            
            slpm_1 = df.at[idx, 'slpm_1']
            slpm_2 = df.at[idx, 'slpm_2']
            df.at[idx, 'slpm_diff'] = slpm_1 - slpm_2
            
            stracc_1 = df.at[idx, 'stracc_1']
            stracc_2 = df.at[idx, 'stracc_2']
            df.at[idx, 'stracc_diff'] = stracc_1 - stracc_2
            
            sapm_1 = df.at[idx, 'sapm_1']
            sapm_2 = df.at[idx, 'sapm_2']
            df.at[idx, 'sapm_diff'] = sapm_1 - sapm_2
            
            strdef_1 = df.at[idx, 'strdef_1']
            strdef_2 = df.at[idx, 'strdef_2']
            df.at[idx, 'strdef_diff'] = strdef_1 - strdef_2
            
            tdavg_1 = df.at[idx, 'tdavg_1']
            tdavg_2 = df.at[idx, 'tdavg_2']
            df.at[idx, 'tdavg_diff'] = tdavg_1 - tdavg_2
            
            tdacc_1 = df.at[idx, 'tdacc_1']
            tdacc_2 = df.at[idx, 'tdacc_2']
            df.at[idx, 'tdacc_diff'] = tdacc_1 - tdacc_2
            
            tddef_1 = df.at[idx, 'tddef_1']
            tddef_2 = df.at[idx, 'tddef_2']
            df.at[idx, 'tddef_diff'] = tddef_1 - tddef_2
            
            subavg_1 = df.at[idx, 'subavg_1']
            subavg_2 = df.at[idx, 'subavg_2']
            df.at[idx, 'subavg_diff'] = subavg_1 - subavg_2
            
            max_streak_1 = df.at[idx, 'max_streak_1']
            max_streak_2 = df.at[idx, 'max_streak_2']
            df.at[idx, 'max_streak_diff'] = max_streak_1 - max_streak_2
            
            cur_streak_1 = df.at[idx, 'cur_streak_1']
            cur_streak_2 = df.at[idx, 'cur_streak_2']
            df.at[idx, 'cur_streak_diff'] = cur_streak_1 - cur_streak_2
            
        df = df.drop(columns=drop_cols, axis=1)
        
        logger.debug("Feature engineering done successfully")
        return df
    except Exception as e:
        logger.error("Failed to do feature engineering %s", e)
        raise

def save_data(df: pd.DataFrame):
    try:
        test, train = train_test_split(df, test_size=0.7, random_state=123, shuffle=False)
        os.makedirs("ml/data/processed", exist_ok=True)
        train.to_csv("ml/data/processed/train_processed.csv", index=False)
        test.to_csv("ml/data/processed/test_processed.csv", index=False)
        
        data_path = os.path.abspath("../../ml/data/processed")
        logger.debug("Saved data in %s", data_path)
    except Exception as e:
        logger.error("Failed to save data %s", e)
        raise     

def main():
    df = pd.read_csv("ml/data/raw/fights_dataset_with_stats.csv")
    df = drop_nas(df)
    df = data_preprocessing(df)
    df = feature_engineering(df)
    
    save_data(df)

if __name__ == "__main__":
    main()
