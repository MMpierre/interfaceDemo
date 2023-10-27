import pandas as pd

####PARAMETERS######

EB = 0  # Experience bonus (%)
RB = 0  # Recency bonus (%)
SB = 0  # Secondary jobs bonus (%)


def compute_scores_P2J(l:list,n:int)->pd.DataFrame:
    df = pd.DataFrame(l)
    df["_score"] = 200 * (df["_score"]-1.43)  #Scaling
    return df.sort_values('_score',ascending=False).drop_duplicates(["_id"])[:n]

def compute_scores_J2P(l:list,n:int)->pd.DataFrame:
    df = pd.DataFrame(l)

    processed_groups = []

    # Step 1: Group by '_id'
    grouped = df.groupby('_id')

    # Step 2: Process each group
    for name, group in grouped:
        group = group
        for i in range(1, 4):
            if i < group.shape[0] + 1:
                group[f'_score{i}'] = group['_score'].shift(-i + 1)
            else: 
                group[f'_score{i}'] = 1
        group = group.head(1)  # Keep only the first row
        processed_groups.append(group)

    # Step 3: Concatenate all processed groups
    final_df = pd.concat(processed_groups).reset_index(drop=True)

    # Drop the original '_score' column if needed
    final_df.drop(columns=['_score'], inplace=True)
    final_df.fillna(1,inplace=True)

    def getLength(dic,string):
        if string in dic.keys():
            return dic[string]
        return 1

    weighted_scores = pd.DataFrame([final_df['_score1'] + RB/50 + EB/900 * final_df['_source'].apply(lambda x: getLength(x,"length1")),
                                    final_df['_score2'] + RB/100 + EB/900 * final_df['_source'].apply(lambda x: getLength(x,"length2")),
                                    final_df['_score3'] + RB/200 + EB/900 * final_df['_source'].apply(lambda x: getLength(x,"length3"))])

    final_df["customWeight"] = weighted_scores.max(axis=0) 

    # Identify index of the max value for each row
    max_indices = weighted_scores.idxmax()
    final_df['non_max_sum'] = 0
    for i, max_idx in max_indices.items():
        non_max_values = [weighted_scores.loc[j, i] for j in range(3) if j != max_idx]
        final_df.loc[i, 'non_max_sum'] = sum(non_max_values) * SB /200
    final_df['customWeight'] += final_df['non_max_sum']
    final_df.drop(columns=['non_max_sum'], inplace=True)

    final_df["_score"] = (final_df["customWeight"] - 1.43)*200
    final_df.drop("customWeight",axis=1)
    return final_df.sort_values('_score',ascending=False)[:n]