from pyrh import Robinhood
import numpy as np
import tulipy as ti 
import sched 
import time

rh = Robinhood()
rh.login(username="EMAIL", password="PASSWORD")


rsiPeriod = 10 #Shorter RSI more reactive, try 10 for less sensitivity
enterTrade = False

scheduler = sched.scheduler(time.time, time.sleep)

def execute(sc):

    global rsiPeriod
    global enterTrade

    print("Printing Quotes...")
    historical_quotes = rh.get_historical_quotes("TSLA", "5minute", "day")

    closePrices = []
    #format close prices for RSI
    currentIndex = 0
    for key in historical_quotes["results"][0]["historicals"]:
        if (currentIndex >= len(historical_quotes["results"][0]["historicals"]) - (rsiPeriod + 1)):
            closePrices.append(float(key['close_price']))
        currentIndex += 1
    STOCK_DATA = np.array(closePrices) # ti to np array

    #Calculate RSI - 30/70 Principle
    print(len(closePrices))
    if (len(closePrices) > (rsiPeriod)):
        rsi = ti.rsi(STOCK_DATA, period=rsiPeriod)
        instrument = rh.instruments("TSLA")[0]
        #Buy order trigger when RSI is less than or equal to 30
        if rsi[len(rsi) - 1] <= 30 and not enteredTrade:
            print("RSI Below 30 - BUY")
            rh.place_buy_order(instrument, 1)
            enteredTrade = True
        #Sell order trigger when RSI greater than or equal to 70
        if rsi[len(rsi) - 1] >= 70 and enteredTrade:
            print("RSI Above 70 - SELL")
            rh.place_sell_order(instrument, 1)
            enteredTrade = False
        print(rsi)
    #Calls method in 5 minute intervals
    scheduler.enter(300, 1, execute, (sc,))

scheduler.enter(1, 1, execute, (scheduler,))

scheduler.run()

