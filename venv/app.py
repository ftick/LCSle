import json
from this import d
from worldsutils import *
from flask import Flask, request, render_template, make_response, url_for, redirect
from datetime import datetime, timedelta, date
import requests
import os

app = Flask(__name__)

API_KEY = os.getenv('API_KEY')
API_STATS_URL = os.getenv('API_STATS_URL')

def getCookieData(daily=""):
    prefix = ""
    if daily:
        prefix = "d_"
    try:
        secret = request.cookies.get(prefix+'secret')
        attempts = int(request.cookies.get(prefix+'attempts'))
        previousGuesses = request.cookies.get(prefix+'game_record')
        maxYear = request.cookies.get(prefix+'max_year')
        maxYear = maxYear if maxYear else 2021
        minYear = request.cookies.get(prefix+'min_year')
        minYear = minYear if minYear else 2011
        previousGuesses = json.loads(previousGuesses)
        gameOver = 1 if len(previousGuesses) > 0 and previousGuesses[-1]["name"] == 1 else 2 if attempts <= 0 else 0
    except:
        previousGuesses = []
        gameOver = 0
        attempts = 8
        minYear = 2011
        maxYear = 2021

    return previousGuesses, gameOver, secret, attempts, minYear, maxYear

def handleGameOver(previousGuesses, gameOver, secret, attempts, daily, minYear, maxYear):
    if not API_KEY or not API_STATS_URL:
        return None
    # Stat collecting: Sends guesses, secret player, remaining attempts and whether it's a daily attempt to stats endpoint.
    datax = {"guesses":[x['Guess'] for x in previousGuesses], "result":gameOver, 
                          "secret":secret, "attempts":attempts, "minYear":minYear, "maxYear":maxYear, "daily":daily, "timestamp":str(datetime.now())}

    return requests.post(API_STATS_URL, headers={"x-api-key":API_KEY, 'message': json.dumps(datax)})

@app.route("/")
def index():
    if 'clear' in request.args or not 'secret' in request.cookies:
        try:
            minyear = int(request.args['minyear'])
            maxyear = int(request.args['maxyear'])

            if minyear > maxyear:
                maxyeart = minyear
                minyear = maxyear
                maxyear = maxyeart
        except:
            minyear = 2011
            maxyear = 2021
            
        resp = make_response(redirect(url_for('index')))
        resp.set_cookie('game_record', "[]")
        resp.set_cookie('min_year', f"{minyear}")
        resp.set_cookie('max_year', f"{maxyear}")
        resp.set_cookie('secret', getPlayer(minyear=minyear, maxyear=maxyear))

        guessesMap = {1:'6', 2:'7', 3:'8', 4:'8', 5:'8', 6:'8', 7:'8', 8:'8', 9:'9', 10:'9', 11:'9'}

        resp.set_cookie('attempts', guessesMap[maxyear-minyear+1])
        resp.set_cookie('total_attempts', guessesMap[maxyear-minyear+1])
        return resp

    previousGuesses, gameOver, secret, attempts, minYear, maxYear = getCookieData()
    mosaic = ""
    mosaic_names = ""

    if gameOver:
        total_attempts = request.cookies.get('total_attempts')
        guesses = len(previousGuesses) if gameOver == 1 else 'X'
        mosaic = f"Worldsle {guesses}/{total_attempts}\\n\\n" +"\\n".join([x['emoji'] for x in previousGuesses])
        mosaic_names = f"Worldsle {guesses}/{total_attempts}\\n\\n" +"\\n".join([x['emoji']+" "+x['Guess'] for x in previousGuesses])
    
    return render_template("index.html", data=previousGuesses, gameOver=gameOver, minYear=minYear, maxYear=maxYear, player=getPlayerList(minyear=minYear, maxyear=maxYear), 
                            secret=secret, error=False, mosaic=mosaic, mosaic_names=mosaic_names, attempts=attempts)

@app.route("/", methods=['POST'])
def guess():
    previousGuesses, gameOver, secret, attempts, minYear, maxYear = getCookieData()

    if(not gameOver):
        if (hint := getHint(request.form['guess'], secret)):
            previousGuesses.append(getHint(request.form['guess'], secret))
            attempts -= 1
        else:
            x = formatSecret(getPlayerInfo(secret))
            return render_template('index.html', data=previousGuesses, gameOver=gameOver, minYear=minYear, maxYear=maxYear, player=getPlayerList(minyear=minYear, maxyear=maxYear), 
                                    secret=secret, secretinfo=x, error=True, mosaic="", mosaic_names="", attempts=attempts)

        gameOver = 1 if previousGuesses[-1]["name"] == 1 else 2 if attempts <= 0 else 0
        if(gameOver):
            handleGameOver(previousGuesses, gameOver, secret, attempts, False, minYear, maxYear)

    total_attempts = request.cookies.get('total_attempts')
    guesses = len(previousGuesses) if gameOver == 1 else 'X'
    mosaic = f"Worldsle {guesses}/{total_attempts}\\n\\n" +"\\n".join([x['emoji'] for x in previousGuesses])
    mosaic_names = f"Worldsle {guesses}/{total_attempts}\\n\\n" +"\\n".join([x['emoji']+" "+x['Guess'] for x in previousGuesses])

    x = formatSecret(getPlayerInfo(secret))
    resp = make_response(render_template('index.html', data=previousGuesses, gameOver=gameOver, minYear=minYear, maxYear=maxYear, player=getPlayerList(minyear=minYear, maxyear=maxYear), 
                                          secret=secret, secretinfo=x, error=False, mosaic=mosaic, mosaic_names=mosaic_names, attempts=attempts))

    resp.set_cookie('game_record', json.dumps(previousGuesses))
    resp.set_cookie('attempts', str(attempts))

    return resp

@app.route("/daily")
def daily():
    if not 'd_secret' in request.cookies:
        resp = make_response(redirect(url_for('daily')))
        expire_date = datetime.combine(datetime.date(datetime.now()-timedelta(hours=10)), datetime.min.time())+timedelta(days=1, hours=10)
        resp.set_cookie('d_game_record', "[]", expires=expire_date)
        resp.set_cookie('d_secret', getPlayer(daily=True), expires=expire_date)
        resp.set_cookie('d_attempts', '8', expires=expire_date)
        resp.set_cookie('d_max_year', '2021', expires=expire_date)
        resp.set_cookie('d_total_attempts', '8', expires=expire_date)
        return resp

    previousGuesses, gameOver, secret, attempts, minyear, maxyear = getCookieData(daily=True)
    
    mosaic = ""
    mosaic_names = ""

    if gameOver:
        day = getDay(secret)
        total_attempts = request.cookies.get('d_total_attempts')
        guesses = len(previousGuesses) if gameOver == 1 else 'X'
        mosaic = f"Worldsle Daily {day} - {guesses}/{total_attempts}\\n\\n" +"\\n".join([x['emoji'] for x in previousGuesses])
        mosaic_names = f"Worldsle Daily {day} - {guesses}/{total_attempts}\\n\\n" +"\\n".join([x['emoji']+" "+x['Guess'] for x in previousGuesses])

    x = formatSecret(getPlayerInfo(secret))
    return render_template("daily.html", data=previousGuesses, gameOver=gameOver, player=getPlayerList(), 
                            secret=secret, secretinfo=x, error=False, mosaic=mosaic, mosaic_names=mosaic_names, attempts=attempts)

@app.route("/daily", methods=['POST'])
def dailyGuess():
    previousGuesses, gameOver, secret, attempts, minYear, maxYear = getCookieData(daily=True)

    if(not gameOver):
        if (hint := getHint(request.form['guess'], secret, daily=True)):
            previousGuesses.append(hint)
            attempts -= 1
        else:
            mosaic = "\n".join([x['emoji'] for x in previousGuesses])
            return render_template('daily.html', data=previousGuesses, gameOver=gameOver, player=getPlayerList(), secret=secret, secretinfo=formatInfo(getPlayerInfo(secret)), error=True, mosaic=mosaic, attempts=attempts)

        gameOver = 1 if previousGuesses[-1]["name"] == 1 else 2 if attempts <= 0 else 0
        if(gameOver):
            handleGameOver(previousGuesses, gameOver, secret, attempts, True, minYear, maxYear)

    total_attempts = request.cookies.get('d_total_attempts')
    guesses = len(previousGuesses) if gameOver == 1 else 'X'
    day = getDay(secret)

    mosaic = f"Worldsle Daily {day} - {guesses}/{total_attempts}\\n\\n" +"\\n".join([x['emoji'] for x in previousGuesses])
    mosaic_names = f"Worldsle Daily {day} - {guesses}/{total_attempts}\\n\\n" +"\\n".join([x['emoji']+" "+x['Guess'] for x in previousGuesses])

    x = formatSecret(getPlayerInfo(secret))
    resp = make_response(render_template('daily.html', data=previousGuesses, gameOver=gameOver, player=getPlayerList(), 
                                          secret=secret, secretinfo=x, error=False, mosaic=mosaic, mosaic_names=mosaic_names, attempts=attempts))
                                          
    resp.set_cookie('d_game_record', json.dumps(previousGuesses))
    resp.set_cookie('d_attempts', str(attempts))

    return resp

if __name__ == "__main__":
    # from waitress import serve
    # serve(app, host="0.0.0.0", port=80)
    app.run(debug=True, use_reloader=True)