import pandas as pd
from sklearn.metrics import classification_report
import pickle as pkl

def main():
    df = pd.read_csv("data/processed/test_processed.csv")
    X_test = df.drop('outcome', axis=1)
    y_test = df.outcome
    
    with open("model.pkl", "rb") as file:
        model = pkl.load(file)
    
    y_pred = model.predict(X_test)
    
    with open('model_logs.txt', 'w') as file:
        file.write(str(classification_report(y_test, y_pred)))
        
if __name__ == '__main__':
    main()
    
    