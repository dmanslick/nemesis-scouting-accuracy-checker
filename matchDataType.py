from typing import List, Dict, Literal
from typing_extensions import TypedDict

class Alliance(TypedDict):
    dq_team_keys: List[str]
    score: int
    surrogate_team_keys: List[str]
    team_keys: List[str]

class ScoreBreakdown(TypedDict):
    adjustPoints: int
    autoAmpNoteCount: int
    autoAmpNotePoints: int
    autoLeavePoints: int
    autoLineRobot1: str
    autoLineRobot2: str
    autoLineRobot3: str
    autoPoints: int
    autoSpeakerNoteCount: int
    autoSpeakerNotePoints: int
    autoTotalNotePoints: int
    coopNotePlayed: bool
    coopertitionBonusAchieved: bool
    coopertitionCriteriaMet: bool
    endGameHarmonyPoints: int
    endGameNoteInTrapPoints: int
    endGameOnStagePoints: int
    endGameParkPoints: int
    endGameRobot1: str
    endGameRobot2: str
    endGameRobot3: str
    endGameSpotLightBonusPoints: int
    endGameTotalStagePoints: int
    ensembleBonusAchieved: bool
    ensembleBonusOnStageRobotsThreshold: int
    ensembleBonusStagePointsThreshold: int
    foulCount: int
    foulPoints: int
    g206Penalty: bool
    g408Penalty: bool
    g424Penalty: bool
    melodyBonusAchieved: bool
    melodyBonusThreshold: int
    melodyBonusThresholdCoop: int
    melodyBonusThresholdNonCoop: int
    micCenterStage: bool
    micStageLeft: bool
    micStageRight: bool
    rp: int
    techFoulCount: int
    teleopAmpNoteCount: int
    teleopAmpNotePoints: int
    teleopPoints: int
    teleopSpeakerNoteAmplifiedCount: int
    teleopSpeakerNoteAmplifiedPoints: int
    teleopSpeakerNoteCount: int
    teleopSpeakerNotePoints: int
    teleopTotalNotePoints: int
    totalPoints: int
    trapCenterStage: bool
    trapStageLeft: bool
    trapStageRight: bool

class MatchData(TypedDict):
    actual_time: int
    alliances: Dict[str, Alliance]
    comp_level: str
    event_key: str
    key: str
    match_number: int
    post_result_time: int
    predicted_time: int
    score_breakdown: Dict[Literal["blue", "red"], ScoreBreakdown]
    set_number: int
    time: int
    videos: List[Dict[str, str]]
    winning_alliance: str