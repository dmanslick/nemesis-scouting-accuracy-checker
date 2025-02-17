from wrappers import MatchScoutingDataWrapper, TBAWrapper
import json
import os
from dotenv import load_dotenv # type: ignore
from matchDataType import MatchData
import numpy as np

load_dotenv()

path = "./inputs/" + input("Enter the file name in the inputs folder: ")
compKey = input("Enter the competition key: ")

rawScoutingData = json.load(open(path))

tbaWrapper = TBAWrapper(compKey, os.getenv('TBA_KEY'))

lastMatchNum = tbaWrapper.lastMatchNum

scoutingData = [[] for _ in range(lastMatchNum)]
scouterAccuraciesRaw = [[] for _ in range(lastMatchNum)]
alliancePerMatchAcc = [{"blue": 0, "red": 0} for _ in range(lastMatchNum)]

for data in rawScoutingData:
    if data['teamNum'] != '' and data['matchNum'] != '':
        matchNum = int((str(data['matchNum']).strip()))
        if (matchNum > len(scoutingData)): continue
        scoutingData[matchNum - 1].append(data)

scoutNames = list(set(d['scoutName'] for d in rawScoutingData))

A = np.zeros((2*lastMatchNum, len(scoutNames)))

b = np.zeros(2*lastMatchNum)

def sumScoutData(scoutData): 
    return scoutData['ampMade_atn'] + scoutData['spkrMade_atn'] + scoutData['ampMade_tp'] + scoutData['spkrMade_tp']

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
    
    index = (matchNum - 1) * 2
    
    b[index] = redAllianceTotalGamePieces
    b[index - 1] = blueAllianceTotalGamePieces
 
    for scoutData in data:
        try: 
            if int(scoutData['teamNum']) in redAllianceTeamNums: 
                A[index, scoutNames.index(scoutData['scoutName'])] = sumScoutData(scoutData)
            else: 
                A[index - 1, scoutNames.index(scoutData['scoutName'])] = sumScoutData(scoutData)
        except: 
            pass

    print("Match Number:", matchNum)
    print("Red Alliance Accuracy: " + str(round(redAllianceAccuracy * 100, 3)) + "%")
    print("Blue Alliance Accuracy: " +  str(round(blueAllianceAccuracy * 100, 3)) + "%")
    print()

x, residuals, rank, singular_values = np.linalg.lstsq(A, b, rcond=None)

coefficients = x.flatten()

scouterAccuraciesEstimated = []

for i in range(len(scoutNames)): 
    acc = round(coefficients[i], 4) * 100
    scouterAccuraciesEstimated.append({'name': scoutNames[i], 'accuracy': acc})

scouterAccuraciesEstimated.sort(key=lambda x: x['accuracy'])

for estimate in scouterAccuraciesEstimated:
    print(str(estimate['name']) + ':', str(estimate['accuracy']) + '%')

# doing abs because somehow some people have negative accuracies even with the corrected formula
avgAccuracy = np.average(list(abs(estimate['accuracy']) for estimate in scouterAccuraciesEstimated))

print('Average accuracy:', str(avgAccuracy) + '%')