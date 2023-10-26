import pandas as pd

#Formattage pour la sortie
def outputFormat(res:pd.DataFrame)->str:
    results = []
    for _,row in res.iterrows():
        result = {"id" : row["_id"],
                  "score" : row["_score"]}
        results.append(result)
    return(str(results))

