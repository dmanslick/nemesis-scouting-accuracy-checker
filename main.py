from typing import List
import numpy as np
import json
import os
from dotenv import load_dotenv
import requests
from matchDataType import MatchData

load_dotenv()

path = "./inputs/" + input("Enter the file name in the inputs folder: ")
compKey = input("Enter the competition key: ")

scoutingData = json.load(open(path))

tbaResponse = requests.get(f"https://www.thebluealliance.com/api/v3/event/{compKey}/matches", headers={'X-TBA-Auth-Key': os.getenv("TBA_KEY") })
tbaData: List[MatchData] = tbaResponse.json()
tbaData: List[MatchData] = list(filter(lambda match: match['comp_level'] != 'f' and match['comp_level'] != 'sf', tbaData))[::-1]
tbaData = sorted(tbaData, key=lambda match: match["match_number"])

for match in tbaData:   
    print(f"The total scores for match: {match['match_number']}")
    print("Blue: " + str(match['score_breakdown']['blue']['totalPoints']))
    print("Red: " + str(match['score_breakdown']['red']['totalPoints']))