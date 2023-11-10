import pandas as pd

#Formattage pour la sortie
def outputFormat(res:pd.DataFrame)->str:
    results = []
    for _,row in res.iterrows():
        result = {"id" : row["_id"],
                  "score" : row["_score"]}
        for i in range(3):
            if f"_score{i}" in row.keys():
                result[f"score{i}"] = row[f"_score{i}"]
        results.append(result)
    return(str(results))



