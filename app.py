import json
from pokeutils import *
from flask import Flask, request, render_template, make_response, url_for, redirect
from datetime import datetime, timedelta, date
import requests
import os

from decouple import config

app = Flask(__name__)

API_KEY = config('API_KEY')
API_STATS_URL = config('API_STATS_URL')

def getCookieData(daily=""):
    prefix = ""
    if daily:
        prefix = "d_"
    try:
        secret = request.cookies.get(prefix+'secret')
        attempts = int(request.cookies.get(prefix+'attempts'))
        previousGuesses = request.cookies.get(prefix+'game_record')
        maxGen = request.cookies.get(prefix+'max_gen')
        maxGen = maxGen if maxGen else 8
        minGen = request.cookies.get(prefix+'min_gen')
        minGen = minGen if minGen else 1
        previousGuesses = json.loads(previousGuesses)
        gameOver = 1 if len(previousGuesses) > 0 and previousGuesses[-1]["name"] == 1 else 2 if attempts <= 0 else 0
    except:
        previousGuesses = []
        gameOver = 0
        attempts = 8
        minGen = 1
        maxGen = 8

    return previousGuesses, gameOver, secret, attempts, minGen, maxGen

def handleGameOver(previousGuesses, gameOver, secret, attempts, daily, minGen, maxGen):
    if not API_KEY or not API_STATS_URL:
        return None
    # Stat collecting: Sends guesses, secret player, remaining attempts and whether it's a daily attempt to stats endpoint.
    message = json.dumps({"guesses":[x['Guess'] for x in previousGuesses], "result":gameOver, 
                          "secret":secret, "attempts":attempts, "minGen":minGen, "maxGen":maxGen, "daily":daily, "timestamp":str(datetime.now())})

    return requests.post(API_STATS_URL, headers={"x-api-key":API_KEY}, json={"message":message})

@app.route("/")
def index():
    if 'clear' in request.args or not 'secret' in request.cookies:
        try:
            mingen = int(request.args['mingen'])
            maxgen = int(request.args['maxgen'])

            if mingen > maxgen:
                maxgent = mingen
                mingen = maxgen
                maxgen = maxgent
        except:
            mingen = 1
            maxgen = 8
            
        resp = make_response(redirect(url_for('index')))
        resp.set_cookie('game_record', "[]")
        resp.set_cookie('min_gen', f"{mingen}")
        resp.set_cookie('max_gen', f"{maxgen}")
        resp.set_cookie('secret', getPlayer(mingen=mingen, maxgen=maxgen))

        guessesMap = {1:'5', 2:'5', 3:'6', 4:'6', 5:'7', 6:'7', 7:'8', 8:'8'}

        resp.set_cookie('attempts', guessesMap[maxgen-mingen+1])
        resp.set_cookie('total_attempts', guessesMap[maxgen-mingen+1])
        return resp

    previousGuesses, gameOver, secret, attempts, minGen, maxGen = getCookieData()
    mosaic = ""
    mosaic_names = ""

    if gameOver:
        total_attempts = request.cookies.get('total_attempts')
        guesses = len(previousGuesses) if gameOver == 1 else 'X'
        mosaic = f"Squirdle {guesses}/{total_attempts}\\n\\n" +"\\n".join([x['emoji'] for x in previousGuesses])
        mosaic_names = f"Squirdle {guesses}/{total_attempts}\\n\\n" +"\\n".join([x['emoji']+" "+x['Guess'] for x in previousGuesses])
    
    return render_template("index.html", data=previousGuesses, gameOver=gameOver, mingen=minGen, maxgen=maxGen, player=getPokeList(mingen=minGen, maxgen=maxGen), 
                            secret=secret, error=False, mosaic=mosaic, mosaic_names=mosaic_names, attempts=attempts)

@app.route("/", methods=['POST'])
def guess():
    previousGuesses, gameOver, secret, attempts, minGen, maxGen = getCookieData()

    if(not gameOver):
        if (hint := getHint(request.form['guess'], secret)):
            previousGuesses.append(getHint(request.form['guess'], secret))
            attempts -= 1
        else:
            return render_template('index.html', data=previousGuesses, gameOver=gameOver, minGen=minGen, maxgen=maxGen, player=getPokeList(mingen=minGen, maxgen=maxGen), 
                                    secret=secret, error=True, mosaic="", mosaic_names="", attempts=attempts)

        gameOver = 1 if previousGuesses[-1]["name"] == 1 else 2 if attempts <= 0 else 0
        if(gameOver):
            handleGameOver(previousGuesses, gameOver, secret, attempts, False, minGen, maxGen)

    total_attempts = request.cookies.get('total_attempts')
    guesses = len(previousGuesses) if gameOver == 1 else 'X'
    mosaic = f"Squirdle {guesses}/{total_attempts}\\n\\n" +"\\n".join([x['emoji'] for x in previousGuesses])
    mosaic_names = f"Squirdle {guesses}/{total_attempts}\\n\\n" +"\\n".join([x['emoji']+" "+x['Guess'] for x in previousGuesses])
    resp = make_response(render_template('index.html', data=previousGuesses, gameOver=gameOver, mingen=minGen, maxgen=maxGen, player=getPokeList(mingen=minGen, maxgen=maxGen), 
                                          secret=secret, error=False, mosaic=mosaic, mosaic_names=mosaic_names, attempts=attempts))

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
        resp.set_cookie('d_max_gen', '8', expires=expire_date)
        resp.set_cookie('d_total_attempts', '8', expires=expire_date)
        return resp

    previousGuesses, gameOver, secret, attempts, minGen, maxGen = getCookieData(daily=True)
    
    mosaic = ""
    mosaic_names = ""

    if gameOver:
        day = getDay(secret)
        total_attempts = request.cookies.get('d_total_attempts')
        guesses = len(previousGuesses) if gameOver == 1 else 'X'
        mosaic = f"Squirdle Daily {day} - {guesses}/{total_attempts}\\n\\n" +"\\n".join([x['emoji'] for x in previousGuesses])
        mosaic_names = f"Squirdle Daily {day} - {guesses}/{total_attempts}\\n\\n" +"\\n".join([x['emoji']+" "+x['Guess'] for x in previousGuesses])

    return render_template("daily.html", data=previousGuesses, gameOver=gameOver, player=getPokeList(), 
                            secret=secret, error=False, mosaic=mosaic, mosaic_names=mosaic_names, attempts=attempts)

@app.route("/daily", methods=['POST'])
def dailyGuess():
    previousGuesses, gameOver, secret, attempts, minGen, maxGen = getCookieData(daily=True)

    if(not gameOver):
        if (hint := getHint(request.form['guess'], secret, daily=True)):
            previousGuesses.append(hint)
            attempts -= 1
        else:
            mosaic = "\n".join([x['emoji'] for x in previousGuesses])
            return render_template('daily.html', data=previousGuesses, gameOver=gameOver, player=getPokeList(), secret=secret, error=True, mosaic=mosaic, attempts=attempts)

        gameOver = 1 if previousGuesses[-1]["name"] == 1 else 2 if attempts <= 0 else 0
        if(gameOver):
            handleGameOver(previousGuesses, gameOver, secret, attempts, True, minGen, maxGen)

    total_attempts = request.cookies.get('d_total_attempts')
    guesses = len(previousGuesses) if gameOver == 1 else 'X'
    day = getDay(secret)

    mosaic = f"Squirdle Daily {day} - {guesses}/{total_attempts}\\n\\n" +"\\n".join([x['emoji'] for x in previousGuesses])
    mosaic_names = f"Squirdle Daily {day} - {guesses}/{total_attempts}\\n\\n" +"\\n".join([x['emoji']+" "+x['Guess'] for x in previousGuesses])

    resp = make_response(render_template('daily.html', data=previousGuesses, gameOver=gameOver, player=getPokeList(), 
                                          secret=secret, error=False, mosaic=mosaic, mosaic_names=mosaic_names, attempts=attempts))
                                          
    resp.set_cookie('d_game_record', json.dumps(previousGuesses))
    resp.set_cookie('d_attempts', str(attempts))

    return resp

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)