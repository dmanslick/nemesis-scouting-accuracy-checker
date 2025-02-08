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
scouterAccuraciesRaw = {}
scouterAccuraciesAvg = {}
alliancePerMatchAcc = [{"blue": 0, "red": 0} for _ in range(lastMatchNum)]

for data in rawScoutingData:
    if data['teamNum'] != '' and data['matchNum'] != '':
        matchNum = int((str(data['matchNum']).strip()))
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
    
    redAllianceTotalGamePieces = tbaWrapper.getAllianceTotalGamePieces(matchNum, 'red')
    blueAllianceTotalGamePieces = tbaWrapper.getAllianceTotalGamePieces(matchNum, 'blue')

    redAllianceAccuracy = scoutingDataWrapper.redAllianceTotalGamePieces / redAllianceTotalGamePieces
    blueAllianceAccuracy = scoutingDataWrapper.blueAllianceTotalGamePieces / blueAllianceTotalGamePieces

    for scoutData in scoutingDataWrapper.blueAllianceRawData:
        if str(scoutData['teamNum']).strip().isdigit():
            teamNum = int(str(scoutData['teamNum']).strip())
            teamOPR = tbaWrapper.getOPR(teamNum)
            robotEstimate = int((tbaWrapper.getOPR(teamNum) / blueAllianceOPR) * blueAllianceTotalGamePieces)
            teamTotalGamePieces = scoutingDataWrapper.getTeamTotalGamePieces(teamNum)
            estimatedInaccuracy = abs(robotEstimate - teamTotalGamePieces) / abs(blueAllianceTotalGamePieces + scoutingDataWrapper.blueAllianceTotalGamePieces)
            estimatedAccuracy = 1 - estimatedInaccuracy
            scoutName = scoutData['scoutName']
            if scoutName in scouterAccuraciesRaw: scouterAccuraciesRaw[scoutName].append(estimatedAccuracy)
            else: scouterAccuraciesRaw[scoutName] = [estimatedAccuracy]

    for scoutData in scoutingDataWrapper.redAllianceRawData:
        if str(scoutData['teamNum']).strip().isdigit():
            teamNum = int(str(scoutData['teamNum']).strip())
            teamOPR = tbaWrapper.getOPR(teamNum)
            robotEstimate = int((tbaWrapper.getOPR(teamNum) / redAllianceOPR) * redAllianceTotalGamePieces)
            teamTotalGamePieces = scoutingDataWrapper.getTeamTotalGamePieces(teamNum)
            estimatedInaccuracy = abs(robotEstimate - teamTotalGamePieces) / abs(redAllianceTotalGamePieces + scoutingDataWrapper.redAllianceTotalGamePieces)
            estimatedAccuracy = 1 - estimatedInaccuracy
            scoutName = scoutData['scoutName']
            if scoutName in scouterAccuraciesRaw: scouterAccuraciesRaw[scoutName].append(estimatedAccuracy)
            else: scouterAccuraciesRaw[scoutName] = [estimatedAccuracy]

for scouter in scouterAccuraciesRaw: scouterAccuraciesAvg[scouter] = sum(scouterAccuraciesRaw[scouter]) / len(scouterAccuraciesRaw[scouter])

print(scouterAccuraciesAvg)