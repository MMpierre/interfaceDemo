# knnSearches
runP2Jsearch.py
    > P2Jsearch(id,n,expected,geo,distance)
    - id of the profil 
    - n number of results
    - geo geolocation of the profil, can be None
    - distance radius of preference of the user, can be None
imports
    computeScore.py
    > compute_scores(l,n)
    - l list of tuples ("mission_id",score)
    - n number of results to return

    getProfilVectors.py
    > getProfilVectors((id,es,index))
    - id of the profil
    - es elasticsearch python client
    - index where the profiles are kept
