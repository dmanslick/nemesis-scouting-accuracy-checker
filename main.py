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

    blueAllianceOPR = tbaWrapper.getAllianceOPR(matchNum, 'blue')
    redAllianceOPR = tbaWrapper.getAllianceOPR(matchNum, 'red')
    blueAllianceTeamNums = tbaWrapper.getAllianceTeamNums(matchNum, 'blue')
    redAllianceTeamNums = tbaWrapper.getAllianceTeamNums(matchNum, 'red')
    
    scoutingDataWrapper = MatchScoutingDataWrapper(redAllianceTeamNums, blueAllianceTeamNums, data)
    
    redAllianceAccuracy = scoutingDataWrapper.redAllianceTotalGamePieces / tbaWrapper.getAllianceTotalGamePieces(matchNum, 'red')
    blueAllianceAccuracy = scoutingDataWrapper.blueAllianceTotalGamePieces / tbaWrapper.getAllianceTotalGamePieces(matchNum, 'blue')
    
    print(scoutingDataWrapper.redAllianceTotalAmpAuto)
    print("Match Number:", matchNum)
    print("Red Alliance Accuracy: " + str(round(redAllianceAccuracy * 100, 3)) + "%")
    print("Blue Alliance Accuracy: " +  str(round(blueAllianceAccuracy * 100, 3)) + "%")
    print()

