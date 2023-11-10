import pandas as pd
import streamlit as st
memory = st.session_state

def compute_scores(l:list,n:int)->pd.DataFrame:

    SC = getParameters()
    df = pd.DataFrame(l)
    df.loc[:,"_score"] = (50*df["_score"]).apply(lambda x: computeScaling(x,SC))
    df.loc[:,"exp"] = pd.Series([i//n for i in range(len(df))])
    return df.sort_values('_score',ascending=False)


def getParameters():
    return memory.SC

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
