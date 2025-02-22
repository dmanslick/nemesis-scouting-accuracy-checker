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

A = np.zeros((8*lastMatchNum, len(scoutNames)))

b = np.zeros(8*lastMatchNum)

def sumScoutData(scoutData): 
    return scoutData['ampMade_atn'] + scoutData['spkrMade_atn'] + scoutData['ampMade_tp'] + scoutData['spkrMade_tp']

def correctZerosMatchData(totalGamepieces):
    if totalGamepieces != 0:
        return totalGamepieces + 3
    else:
        return totalGamepieces

def correctZerosScoutData(totalGamepieces, scoutGamepieces):
    if totalGamepieces != 0:
        return scoutGamepieces + 1
    else:
        return scoutGamepieces

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
    
    index = (matchNum - 1) * 8

    b[index] = correctZerosMatchData(tbaWrapper.getAllianceAmpCountAuto(matchNum, 'red'))
    b[index+1] = correctZerosMatchData(tbaWrapper.getAllianceSpkrCountAuto(matchNum, 'red'))
    b[index+2] = correctZerosMatchData(tbaWrapper.getAllianceAmpCountTeleop(matchNum, 'red'))
    b[index+3] = correctZerosMatchData(tbaWrapper.getAllianceSpkrCountTeleop(matchNum, 'red'))
    b[index+4] = correctZerosMatchData(tbaWrapper.getAllianceAmpCountAuto(matchNum, 'blue'))
    b[index+5] = correctZerosMatchData(tbaWrapper.getAllianceSpkrCountAuto(matchNum, 'blue'))
    b[index+6] = correctZerosMatchData(tbaWrapper.getAllianceAmpCountTeleop(matchNum, 'blue'))
    b[index+7] = correctZerosMatchData(tbaWrapper.getAllianceSpkrCountTeleop(matchNum, 'blue'))
 
    for scoutData in data:
        try: 
            if int(scoutData['teamNum']) in redAllianceTeamNums: 
                A[index, scoutNames.index(scoutData['scoutName'])] = correctZerosScoutData(b[index], scoutData['ampMade_atn'])
                A[index+1, scoutNames.index(scoutData['scoutName'])] = correctZerosScoutData(b[index+1], scoutData['spkrMade_atn'])
                A[index+2, scoutNames.index(scoutData['scoutName'])] = correctZerosScoutData(b[index+2], scoutData['ampMade_tp'])
                A[index+3, scoutNames.index(scoutData['scoutName'])] = correctZerosScoutData(b[index+3], scoutData['spkrMade_tp'])

            else: 
                A[index + 4, scoutNames.index(scoutData['scoutName'])] = correctZerosScoutData(b[index+4], scoutData['ampMade_atn'])
                A[index + 5, scoutNames.index(scoutData['scoutName'])] = correctZerosScoutData(b[index+5], scoutData['spkrMade_atn'])
                A[index + 6, scoutNames.index(scoutData['scoutName'])] = correctZerosScoutData(b[index+6], scoutData['ampMade_tp'])
                A[index + 7, scoutNames.index(scoutData['scoutName'])] = correctZerosScoutData(b[index+7], scoutData['spkrMade_tp'])

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
    if acc > 100: acc = -acc + 200
    scouterAccuraciesEstimated.append({'name': scoutNames[i], 'accuracy': acc})

scouterAccuraciesEstimated.sort(key=lambda x: x['accuracy'])

for estimate in scouterAccuraciesEstimated:
    print(str(estimate['name']) + ':', str(estimate['accuracy'].round(2)) + '%')

# doing abs because somehow some people have negative accuracies even with the corrected formula
medianAccuracy = np.median(list(abs(estimate['accuracy']) for estimate in scouterAccuraciesEstimated)).round(2)

print('Median scout accuracy:', str(medianAccuracy) + '%')