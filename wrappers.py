import os
from typing import List, Literal
from matchDataType import MatchData
import requests # type: ignore
from matchDataType import ScoreBreakdown

class TBAWrapper:
    def TBAfetcher(self, url: str): 
        return requests.get(url, headers={'X-TBA-Auth-Key': os.getenv("TBA_KEY") })

    def __init__(self, compKey: str, tbaAuthKey: str):
        tbaResponse = self.TBAfetcher(f"https://www.thebluealliance.com/api/v3/event/{compKey}/matches")
        tbaOPRsResponse = self.TBAfetcher(f"https://www.thebluealliance.com/api/v3/event/{compKey}/oprs")

        tbaData: List[MatchData] = tbaResponse.json()
        tbaData: List[MatchData] = list(filter(lambda match: match['comp_level'] != 'f' and match['comp_level'] != 'sf', tbaData))[::-1]
        tbaData: List[MatchData] = sorted(tbaData, key=lambda match: match["match_number"])
        
        self.tbaData = tbaData
        self.tbaOPRs = tbaOPRsResponse.json()['oprs']
        self.lastMatchNum = tbaData[len(tbaData) - 1]['match_number']

    def getMatchData(self, matchNum: int): return self.tbaData[matchNum - 1]

    def getOPR(self, teamNum: int) -> float: 
        key = "frc" + str(teamNum)
        return self.tbaOPRs[key]

    def getAllianceTeamNums(self, matchNum: int, alliance: Literal['blue', 'red']) -> List[int]:
        teamNums = []
        for team in self.getMatchData(matchNum)['alliances'][alliance]['team_keys']: teamNums.append(int(team.replace('frc', '')))
        return teamNums

    def getAllianceOPR(self, matchNum: int, alliance: Literal['blue', 'red']):
        total = 0
        for teamNum in self.getAllianceTeamNums(matchNum, alliance): total += self.getOPR(teamNum)
        return total

    def getAllianceScoreBreakdown(self, matchNum: int, alliance: Literal['blue', 'red']) -> ScoreBreakdown: return self.getMatchData(matchNum)['score_breakdown'][alliance]
       
    def getAllianceAmpCountAuto(self, matchNum: int, alliance: Literal['blue', 'red']) -> int: 
        return self.getAllianceScoreBreakdown(matchNum, alliance)['autoAmpNoteCount'] 
    
    def getAllianceSpkrCountAuto(self, matchNum: int, alliance: Literal['blue', 'red']) -> int: 
        return self.getAllianceScoreBreakdown(matchNum, alliance)['autoSpeakerNoteCount'] 

    def getAllianceAmpCountTeleop(self, matchNum: int, alliance: Literal['blue', 'red']) -> int: 
        return self.getAllianceScoreBreakdown(matchNum, alliance)['teleopAmpNoteCount'] 

    def getAllianceSpkrCountTeleop(self, matchNum: int, alliance: Literal['blue', 'red']) -> int: 
        return self.getAllianceScoreBreakdown(matchNum, alliance)['teleopSpeakerNoteCount'] + self.getAllianceScoreBreakdown(matchNum, alliance)['teleopSpeakerNoteAmplifiedCount']

class MatchScoutingDataWrapper:
    def __init__(self, redAllianceTeamNums, blueAllianceTeamNums, data): 
        self.redAllianceRawData = list(filter(lambda x: str(x['teamNum']).strip().isdigit() and int(x['teamNum']) not in redAllianceTeamNums, data))
        self.blueAllianceRawData = list(filter(lambda x: str(x['teamNum']).strip().isdigit() and int(x['teamNum']) not in blueAllianceTeamNums, data))
        
        self.scoutedRedAllianceTotalAmpAuto = sum(int(item['ampMade_atn']) for item in self.redAllianceRawData)
        self.scoutedBlueAllianceTotalAmpAuto = sum(int(item['ampMade_atn']) for item in self.blueAllianceRawData)

        self.scoutedRedAllianceTotalSpkrAuto = sum(int(item['spkrMade_atn']) for item in self.redAllianceRawData)
        self.scoutedBlueAllianceTotalSpkrAuto = sum(int(item['spkrMade_atn']) for item in self.blueAllianceRawData)

        self.scoutedRedAllianceTotalAmpTeleop = sum(int(item['ampMade_teleop']) for item in self.redAllianceRawData)
        self.scoutedBlueAllianceTotalAmpTeleop = sum(int(item['ampMade_teleop']) for item in self.blueAllianceRawData)

        self.scoutedRedAllianceTotalSpkrTeleop = sum(int(item['spkrMade_teleop']) for item in self.redAllianceRawData)
        self.scoutedBlueAllianceTotalSpkrTeleop = sum(int(item['spkrMade_teleop']) for item in self.blueAllianceRawData)
