import numpy as np
import os
from datetime import datetime, timedelta

def readDex(minyear=2011, maxyear=2021):
    file_name = 'data/{0}-{1}.csv'.format(str(minyear), str(maxyear))
    dex = ''
    if (os.path.exists(file_name)):
        dex = np.recfromcsv(file_name, encoding="utf-8")
        dex = dex[(dex['year'] <= int(maxyear)) & (dex['year'] >= int(minyear))]
    else:
        dex = np.recfromcsv("worldsdex.csv", encoding="utf-8")
        dex = dex[(dex['year'] <= int(maxyear)) & (dex['year'] >= int(minyear))]
        names = []
        data = []
        for entry in dex:
            # print(entry)
            if (entry.name not in names):
                names.append(entry.name)
                data.append(dex[(dex['name'] == entry.name)][0])
        with open(file_name, "w", encoding="utf-8") as write_file:
            write_file.writelines("record,name,year,debut,region,team,pos,gp,k\n")
            for entry in data:
                write_file.writelines('{0},{1},{2},{3},{4},{5},{6},{7},{8}\n'.format(entry.record,entry.name,entry.year,entry.debut,entry.region,entry.team,entry.pos,entry.gp,entry.k))
        dex = np.recfromcsv(file_name, encoding="utf-8")
        dex = dex[(dex['year'] <= int(maxyear)) & (dex['year'] >= int(minyear))]
    return dex

def getPlayer(minyear=2011, maxyear=2021, daily=False):
    if daily:
        today = str(datetime.date(datetime.now()-timedelta(hours=10)))
        dex = np.recfromcsv("daily.csv", encoding="utf-8")
        row = dex[dex['date'] == today]
        secret = row['player'][0]
    else:
        dex = readDex(minyear=2011, maxyear=2021)
        secret = np.random.choice(dex, 1)['name'][0]
        print(secret)
    return secret

def getPlayerList(minyear=2011, maxyear=2021):
    dex = readDex(minyear, maxyear)
    return list(dex.name)

def getDay(pkmn):
    today = str(datetime.date(datetime.now()-timedelta(hours=10)))
    dex = np.recfromcsv("daily.csv", encoding="utf-8")
    return list(dex['date']).index(today)
    
def getPlayerInfo(player):
    dex = readDex()
    return dex[dex['name']==player][0]

def getHint(guess_str, secret_str, daily=False):
    try:
        guess = getPlayerInfo(guess_str)
        secret = getPlayerInfo(secret_str)
        hint = dict()
        if not daily:
            hint['Debut'] = '🟩' if guess["debut"] == secret["debut"] else '🔼' if guess["debut"] < secret["debut"] else '🔽'
        else:
            hint['Debut'] = '🟩' if guess["debut"] == secret["debut"] else '🟦'

        hint['Region'] = '🟩' if guess["region"] == secret["region"] else '🟥'
        hint['Team'] = '🟩' if guess["team"] == secret["team"] else '🟥'
        hint['Role'] = '🟩' if guess["pos"] == secret["pos"] else '🟥'
        hint['Games Played'] = '🟩' if guess["gp"] == secret["gp"] else '🔼' if guess["gp"] < secret["gp"] else '🔽'
        hint['Kills'] = '🟩' if guess["k"] == secret["k"] else '🔼' if guess["k"] < secret["k"] else '🔽'
        hint['emoji'] = getHintMoji(hint)
        hint['name'] = 1 if guess_str == secret_str else 5
        hint['Guess'] = guess_str
        hint['playerinfo'] = formatInfo(guess)
        return hint
    except:
        return False

def getHintMoji(hint):
    return "".join([val for x,val in hint.items()])

def formatInfo(player):
    txt = f"<b>Worlds Debut:</b> {player['debut']}<br>"
    txt += f"<b>Recent Region:</b> {player['region']}<br>"
    txt += f"<b>Recent Team:</b> {player['team']}<br>"
    txt += f"<b>Recent Role:</b> {player['pos']}<br>"
    txt += f"<b>Games Played:</b> {player['gp']}<br>"
    txt += f"<b>Kills:</b> {player['k']}<br>"

    return txt
