import pandas as pd

####PARAMETERS######

EB = 2  # Experience bonus (%)
RB = 2  # Recency bonus (%)
SB = 2  # Secondary jobs bonus (%)


def compute_scores(l:list,n:int)->pd.DataFrame:
    df = pd.DataFrame(l)
    df["_score"] = 200 * (df["_score"]-1.45)  #Scaling
    return df.sort_values('_score',ascending=False).drop_duplicates(["_id"])[:n]

