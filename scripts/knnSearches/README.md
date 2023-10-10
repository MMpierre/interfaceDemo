# Les deux scripts de "matching":
- J2P = Job to Profiles
    - Input : Mission ID, Number of Profiles to return
    - Output : json list - [{"id" : ID, "score": SCORE}, ...]
- P2J = Profile to Jobs
    - Input : Profile ID, Number of Missions to return
    - Outputs : json list - [{"id": ID, "score": SCORE}, ...]

exemple d'appel :
python 5-minutes-profile-1/services/matchpy/scripts/runJ2Psearch.py "218161-2023-08-11" 10
python 5-minutes-profile-1/services/matchpy/scripts/runP2Jsearch.py 5 10
