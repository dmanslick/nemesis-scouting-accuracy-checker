from wrappers import MatchScoutingDataWrapper, TBAWrapper
import json
import os
from dotenv import load_dotenv # type: ignore
from matchDataType import MatchData

load_dotenv()

path = "./inputs/" + input("Enter the file name in the inputs folder: ")
compKey = input("Enter the competition key: ")

rawScoutingData = json.load(open(path))

tbaWrapper = TBAWrapper(compKey, os.getenv('TBA_KEY'))

lastMatchNum = tbaWrapper.lastMatchNum

scoutingData = [[] for _ in range(lastMatchNum)]
scouterAccuraciesRaw = [[] for _ in range(lastMatchNum)]
scouterAccuraciesAvg = {}
alliancePerMatchAcc = [{"blue": 0, "red": 0} for _ in range(lastMatchNum)]

for data in rawScoutingData:
    matchNum = int(data['matchNum'])
    if (matchNum > len(scoutingData)): continue
    scoutingData[matchNum - 1].append(data)

for data in scoutingData:
    try: 
        data[0]
    except:
        continue    

    matchNum = int(data[0]['matchNum'])

    blueAllianceOPR = tbaWrapper.getBlueAllianceOPR(matchNum)
    redAllianceOPR = tbaWrapper.getRedAllianceOPR(matchNum)
    blueAllianceTeamNums = tbaWrapper.getBlueAllianceTeamNums(matchNum)
    redAllianceTeamNums = tbaWrapper.getRedAllianceTeamNums(matchNum)
    
    scoutingDataWrapper = MatchScoutingDataWrapper(redAllianceTeamNums, blueAllianceTeamNums, data)
    
    