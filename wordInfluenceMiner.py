#!/usr/bin/python3
   
   
exec(open("universalFunctions.py").read())


def getTwitterPosts():
   import tweepy
   import time
   from datetime import datetime
   import string
   tweets = {}
   
   config = getConfig()
   period = config["period"]
   coinNames = list(getCoinNames())
   api = initTwitterApi("Miner")
   sinceDate = datetime.fromtimestamp(time.time() - period * 2).strftime('%Y-%m-%d')
   untilDate = datetime.fromtimestamp(time.time() - period).strftime('%Y-%m-%d')
   for coin in coinNames:
      for tweet in tweepy.Cursor(api.search, q=coin, tweet_mode="extended", until=untilDate, since=sinceDate, lang="en").items(1000):
         tweetText = removeText(tweet._json["full_text"]).lower().strip()
         tweetText = "".join([item for item in list(tweetText) if item not in list(string.punctuation + "#!()-$@/'?")])
         tweets[tweetText] = tweet._json["user"]["id"]
   return tweets


def getPriceMovement():
   import time
   from poloniex import Poloniex
   coinNames = getCoinNames()
   config = getConfig()
   polo = Poloniex()
   coinPriceChanges = {}
   period = config["period"]
   for coin in coinNames:
      startTime = time.time() - period
      coinWtdAvg = float(polo.returnChartData(coinNames[coin], start=startTime)[0]["weightedAverage"])
      lastCoinWtdAvg = float(polo.returnChartData(coinNames[coin], start=startTime - period, end=startTime)[0]["weightedAverage"])
      changePercent = coinWtdAvg / lastCoinWtdAvg - 1
      coinPriceChanges[coin] = changePercent
   return coinPriceChanges


def getWordInfluences():
   wordInfluences = {}
   coinPriceChanges = getPriceMovement()
   wordFrequencies = getWordFrequencies()
   for coin in wordFrequencies:
      coinPriceChange = coinPriceChanges[coin]
      for word in wordFrequencies[coin].keys():
         if not word in wordInfluences.keys():
            wordInfluences[word] = [0, 0]
         totalInfluence, incrementCount = wordInfluences[word]
         wordInfluence = wordFrequencies[coin][word] * coinPriceChange
         wordInfluences[word] = [totalInfluence + wordInfluence, incrementCount + 1]
   return wordInfluences


def updateFile(outputFile="wordInfluences.json"):
   import json
   config = getConfig()
   wordInfluences = getWordInfluences()
   try:
      wordInfluencesFile = json.loads(open(outputFile).read())
   except: wordInfluencesFile = {}
   for word in wordInfluences:
      if not word in wordInfluencesFile:
         wordInfluencesFile[word] = [0, 0]
      totalInfluence, incrementCount = wordInfluencesFile[word]
      wordInfluencesFile[word] = [totalInfluence + wordInfluences[word][0], incrementCount + wordInfluences[word][1]]
   wordInfluencesFile = removeStopWords(wordInfluencesFile)
   with open(outputFile, "w") as wordInfluencesFileObj:
      wordInfluencesFileObj.write(json.dumps(wordInfluencesFile, indent=2, sort_keys=True))


def loop():
   while True:
      sleepForPeriod()
      while True:
         try:
            updateFile()    
            break
         except:
            logError()


if __name__ == "__main__":
   loop()
   #updateFile(outputFile="testWordInfluences.json") #Debugging
   #updateFile()

#Made by Alexpimania 2017
