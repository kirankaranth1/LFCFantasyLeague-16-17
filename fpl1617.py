import re
import requests
import json
import math
import time
import os
from operator import itemgetter
import traceback


# Parses members of each team from file
def get_all_teams(filenamePath):
    myFile=open(filenamePath)
    lines=myFile.readlines()
    
    for i in range(0,len(lines)):
        if lines[i].startswith("Team:"):
            
            teamName=str(lines[i]).strip().split(':')[1].strip()
            teams[teamName]=[]
            for j in range(i+1,i+7):
                
                playerName=str(lines[j]).strip().split(',')[0]
                playerID=str(lines[j]).strip().split(',')[1]
                teams[teamName].append([playerName,playerID,1])
    return teams
    
def isValid(playername,fstream):
    return True
    
def Captain_ViceCaptainSetup(teams):
    for k,v in sorted(teams.items()):
        team=k
        print("Team: %s" %(str(k)))
        for i in range(0,len(v)):
            print(str(i+1)+". "+teams[k][i][0])
        captain=int(input("Enter Captain number: "))
        teams[k].append(captain-1)
        if(isValid(teams[k][captain-1][0],f_captain)):
            teams[k][captain-1][2]=2.0
        vc=int(input("Enter vc number: "))
        teams[k].append(vc-1)
        if(isValid(teams[k][vc-1][0],f_vicecaptain)):
            teams[k][vc-1][2]=1.5
    return teams
    
def getTeamScoresfromList(TeamList):
    orignalScore=[]
    orignalScoreDict=[]
    multiplierScore=[]
    multiplierScoreDict=[]
    for player in TeamList[0:6]:
        player_score=get_player_score(player[1],gw)
        orignalScore.append(player_score)
        orignalScoreDict.append({player[0]:player_score})
        multiplierScore.append(player_score*player[2])
        multiplierScoreDict.append({player[0]:player_score*player[2]})
    return(orignalScore,multiplierScore,orignalScoreDict,multiplierScoreDict)
    
# Get a player's score given player ID and gw number
def get_player_score(id,gw):
    url="https://fantasy.premierleague.com/drf/entry/"+str(id)+"/event/"+str(gw)+"/picks"
    r = requests.get(url)
    result = json.loads(r.text)
    points=result['entry_history']['points']
    deductions=result['entry_history']['event_transfers_cost']
    
    score = int(points)-int(deductions)
    return score


    
def isHome(teamname,fixtures):
    for fixture in fixtures:
        
        if teamname in fixture['homeTeamName']:
            return True
        elif teamname in fixture['awayTeamName']:
            return False
        else:
            continue
    
def getfix(gw):
    res = requests.get("http://www.football-data.org/soccerseasons/426/fixtures?matchday="+str(gw))
    result=json.loads(res.text)
    return result['fixtures']

def calcResult(n):
    score=(int(math.floor(n / 10.0)) * 10)/10
    return int(score)

def calcbonus(m):
    if m<=89:
        return 0
    elif m>= 90 and m<129:
        return 1
    elif m>= 130 and m<149: 
        return 2
    else:
        return 3 

try:
    print("-----------------------------------------------------")
    print("LFC India Fantasy League Score calculator 16-17")
    print("Author: kirankaranth1@gmail.com")
    print("-----------------------------------------------------")
    curr_dir=str(os.getcwd())
    teams={}
            
    gw=int(input("Enter Gameweek number: "))
    fixtures=getfix(gw)

    # Streams to all log files
    os.makedirs("TeamScores", exist_ok=True)
    os.makedirs("Results", exist_ok=True)
    os.makedirs("Counts", exist_ok=True)
    os.makedirs("Counts/Captains", exist_ok=True)
    os.makedirs("Counts/ViceCaptains", exist_ok=True)

    teamscores_path=curr_dir+"\TeamScores\TeamScore_gw"+str(gw)+".txt"
    results_path=curr_dir+"\Results\Results_gw"+str(gw)+".txt"
    captain_path=curr_dir+"\Counts\Captains\CaptainCount_gw"+str(gw)+".txt"
    vicecaptain_path=curr_dir+"\Counts\ViceCaptains\ViceCaptainCount_gw"+str(gw)+".txt"


    f_teamscores=open("TeamScores/TeamScore_gw"+str(gw)+".txt",'w')
    f_results=open("Results/Results_gw"+str(gw)+".txt",'w')
    f_captain=open("Counts/Captains/CaptainCount_gw"+str(gw)+".txt",'w')
    f_vicecaptain=open("Counts/ViceCaptains/ViceCaptainCount_gw"+str(gw)+".txt",'w')

    teams=get_all_teams("Test.txt")
    C_teams=Captain_ViceCaptainSetup(teams)
    allTeamScores = {}

    for k,v in sorted(C_teams.items()):
        print("\nCalculating Scores of %s" %(str(k)))
        print("Team: %s" %(str(k)),file=f_teamscores)
        (original,multiplied,oDict,mDict)=getTeamScoresfromList(v)
        max_score=max(original)
        if isHome(str(k),fixtures):
            HA=0.2
            print("Home Advantage: YES",file=f_teamscores)
            home=True
        else:
            HA=0
            print("Home Advantage: NO",file=f_teamscores)
            home=False
        #print(v)
        print("Captain: %s" %(v[v[6]][0]),file=f_teamscores)
        print("Vice Captain: %s" %(v[v[7]][0]),file=f_teamscores)
        print("Individual Scores           : %s" %(str(oDict)),file=f_teamscores)
        print("Team Scores afer multipliers: %s" %(str(mDict)),file=f_teamscores)
        t_score=sum(multiplied)+(HA*max_score)
        print("Cumulative team Score: %s\n" %(str(round(t_score))),file=f_teamscores)
        allTeamScores[str(k)]=round(t_score)
        
    f_teamscores.close()
        
    for fixture in fixtures:
        try:
            hscore=allTeamScores[fixture['homeTeamName']]
            ascore=allTeamScores[fixture['awayTeamName']]
            
            if(9>=math.fabs(hscore-ascore)>=0):
                fixture['result']['goalsAwayTeam']=0
                fixture['result']['goalsHomeTeam']=0
                diff=math.fabs(hscore-ascore)
            elif(hscore-ascore>=10):
                fixture['result']['goalsAwayTeam']=0
                diff=hscore-ascore
                fixture['result']['goalsHomeTeam']=calcResult(diff)
            else:
                diff=ascore-hscore
                fixture['result']['goalsAwayTeam']=calcResult(diff)
                fixture['result']['goalsHomeTeam']=0
                
            print(str(fixture['homeTeamName'])+" vs "+str(fixture['awayTeamName']),file=f_results)
            print(str(allTeamScores[fixture['homeTeamName']])+"-"+str(allTeamScores[fixture['awayTeamName']]),file=f_results)
            print("\nBonus points:"+str(calcbonus(diff)),file=f_results)
            print("Final Score: "+str(fixture['result']['goalsHomeTeam'])+"-"+str(fixture['result']['goalsAwayTeam']),file=f_results)
            print("--------------------------------------------",file=f_results)
        
        except KeyError:
            continue

    f_results.close()
    captains={}
    vicecaptains={}
    isCountsCalculated=True
    for i in range(1,gw+1):
        try:
            currentFile = open("TeamScores/TeamScore_gw"+str(i)+".txt",'r')
        except FileNotFoundError:
            print("WARNING: File TeamScores/TeamScore_gw"+str(i)+".txt not found. Skipping captain and vc count calculation.")
            isCountsCalculated=False
            break
        fileLines = currentFile.readlines()
        for line in fileLines:
            if(line.startswith("Captain")):
                try:
                    captains[line.split(':')[1].strip()] += 1
                except KeyError:
                    captains[line.split(':')[1].strip()] = 1
            if(line.startswith("Vice Captain")):
                try:
                    vicecaptains[line.split(':')[1].strip()] += 1
                except KeyError:
                    vicecaptains[line.split(':')[1].strip()] = 1
        currentFile.close()

    template = "{0:25}:{1:10}"
    if(isCountsCalculated):
        for k,v in sorted(captains.items(), key=itemgetter(1), reverse=True):
            print(template.format(k,v),file=f_captain)

        for k,v in sorted(vicecaptains.items(), key=itemgetter(1), reverse=True):
            print(template.format(k,v),file=f_vicecaptain)
        
    print("\n")
    print("--------------------------------------------------------------------------------------------------")
    print("Team scores are logged at the below location:")
    print(teamscores_path)
    print("------------------------")
    print("Final results are logged at the below location:")
    print(results_path)
    if(isCountsCalculated):
        print("------------------------")
        print("Captain counts are logged at the below location:")
        print(captain_path)
        print("------------------------")
        print("Vice captain counts are logged at the below location:")
        print(vicecaptain_path)
    print("--------------------------------------------------------------------------------------------------")
    dummy=input("Press Enter to exit the program...")

except:
    print("-----------------------------------------------------\n-----------------------------------------------------")
    print("Unexpected error encountered. Please report the below message to author.")
    print(str(traceback.format_exc()))
    dummy=input("Press Enter to exit the program...")