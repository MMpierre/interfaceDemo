import openai
import yaml
import pandas as pd 
import re
import tiktoken
from tqdm import tqdm
import json
from sentence_transformers import SentenceTransformer
def count_tokens(string):
    encoding = tiktoken.encoding_for_model("gpt-4")
    tokens = encoding.encode(string)
    return len(tokens)

config = yaml.safe_load(open("services/matchpy/config.yaml", "r"))
openai.api_key = config["openai"]["key"]

requestA = '''
Je veux que tu récupère les certifications requises  et uniquement les certifications requises pour une offre d'emploi, sous la forme d'une liste Python: 
USER:
Votre agence PROMAN SALON DE PROVENCE recherche pour l'un de ses clients 10 préparateurs de commandes CACES 1B H/F sur Salon.Vos missions consisteront à :- Réaliser le prélèvement des produits selon les instructions de préparation de commande,- Charger des marchandises, des produits.- Acheminer des marchandises en zone d'expédition, de stockage ou de production.- Gérer les préparations de commande  Salaire :  €/h + Prime de productivité + panier + IFM + Congés payés + CET 5% 4h-11h ou 11h-18h ou 10h-17h Pour plus d'offres d'emploi, téléchargez notre application myPROMAN intérimaires sur App Store ou Google Play.vous possédez le CACES 1B.Votre dynamisme, votre savoir-être vous permettront de mener à bien votre mission.  Idéalement, vous avez une première expérience dans ce domaine.Votre dynamisme et vos connaissances sur les gestes et postures à adopter pour exercer ce métier vous permettront de mener à bien votre mission.  Vous êtes sérieux et rigoureux, vous souhaitez vous investir sur du long terme.Cette offre vous intéresse ?Vous pouvez postuler directement sur notre site, ou venir sans rendez-vous, avec un CV à jour. Nous vous attendons à l’agence ! :)A très vite !! ~ Vous pourrez bénéficier d’acompte à la semaine si besoin et d'aides et de services dédiés (mutuelle, déplacement, garde enfant, logement...). ~ Tous nos postes sont ouverts aux personnes en situation de handicap.
CHATGPT:
["CACES 1B"]
USER:\n'''
requestB = "\nCHATGPT:"
import json

usageIN = 0
usageOUT = 0
missions = pd.DataFrame(json.load(open("data/promanMissions/promanMissions.json","r")))

text = ""
for _,description in tqdm(missions.sample(10)["description"].items(),desc="Querying GPT-4",total=5):
        desc = re.sub(re.compile('<.*?>'), '', description[0]["value"])
        request = requestA + desc + requestB
        try:
            response = openai.ChatCompletion.create(model="gpt-4",
                                           messages=[{"role": "user", "content": request}])
            usageIN  += count_tokens(request)
            usageOUT  += response["usage"]["total_tokens"] - count_tokens(request)
        except:
            print("erreur")
        text += desc + "\n\n" + response['choices'][0]["message"]["content"] + "\n\n"


text += f"\n\n Prix total : {usageIN*0.0015/1000 + usageOUT*0.002/1000}$"
text += f"\nPrix IN : {usageIN*0.0015/1000 }$, Prix OUT : {usageOUT*0.002/1000}$"
            

# Open a file in write mode ('w')
with open('services/matchpy/parsing/outputs/gpt_test FS.txt', 'w') as file:
    # Write content to the file
    file.write(text)
