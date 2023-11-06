import pandas as pd
import streamlit as st
memory = st.session_state

def compute_scores(l:list,n:int)->pd.DataFrame:
    SC,EB,SB,LMB = getParameters()
    df = pd.DataFrame(l)
    
    processed_groups = []

    # Step 1: Group by '_id'
    grouped = df.groupby('_id')

    # Step 2: Process each group
    for name, group in grouped:
        group = group
        for i in range(1, 4):
            if i < group.shape[0] + 1:
                group[f'_score{i}'] = max(1,computeScaling(group['_score'].shift(-i + 1)*50,SC).iloc[0])
            else: 
                group[f'_score{i}'] = 1
        group = group.head(1)  # Keep only the first row
        processed_groups.append(group)

    # Step 3: Concatenate all processed groups
    final_df = pd.concat(processed_groups).reset_index(drop=True)

    # Drop the original '_score' column if needed
    final_df.drop(columns=['_score'], inplace=True)
    final_df.fillna(1,inplace=True)

    final_df["_score"] = computeBonus(final_df[["_score1","_score2","_score3"]],SB)

    return final_df.sort_values('_score',ascending=False)[:n]


def getParameters():
    return memory.SC,memory.EB,memory.SB,memory.LMB

def computeScaling(original_score, SC):
    new_score = ((original_score - (SC * 7)) / (100 - (SC * 7))) * 100
    return new_score

def computeBonus(df,SB):

    df.loc[:,'customWeight']  = df[["_score1","_score2","_score3"]].max(axis=1) 

    # Identify index of the max value for each row
    max_indices = df[["_score1","_score2","_score3"]].idxmax(axis=1) 
    df.loc[:,'non_max_sum'] = 0
    for i, max_idx in max_indices.items():
        non_max_values = [df[["_score1","_score2","_score3"]].iloc[i, j] for j in range(3) if j != (int(max_idx[-1])-1)]
        df.loc[i, 'non_max_sum'] = max(0,sum(non_max_values) * SB /100)

    df.loc[:,'customWeight'] += df['non_max_sum']
    df.drop(columns=['non_max_sum'], inplace=True)

    return df['customWeight']

# def experienceBonus(df,EB):
#     weighted_scores = [row['_score1'] +  EB/900 * row['_source'].apply(lambda x: getLength(x,"length1")),
#                         row['_score2'] +  EB/900 * row['_source'].apply(lambda x: getLength(x,"length2")),
#                         row['_score3'] +  EB/900 * row['_source'].apply(lambda x: getLength(x,"length3"))]
