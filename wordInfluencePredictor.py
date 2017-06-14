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
   coinNames = ["siacoin"]#list(getCoinNames())
   api = initTwitterApi("Predictor")
   sinceDate = datetime.fromtimestamp(time.time() - period).strftime('%Y-%m-%d')
   for coin in coinNames:
      for tweet in tweepy.Cursor(api.search, q=coin, tweet_mode="extended", since=sinceDate, lang="en").items(1000):
         tweetText = removeText(tweet._json["full_text"]).lower().strip()
         "".join([item for item in list(tweetText) if item not in list(string.punctuation)])
         tweets[tweetText] = tweet._json["user"]["id"]
   return tweets
      
      
def getAvgWordScore(wordInfluences, wordFrequencies):
   totalWordFrequency = totalWordScore = 0
   for coin in wordFrequencies:
      for word in wordFrequencies[coin]:
         if word in wordInfluences:
            wordFrequency = wordFrequencies[coin][word]
            wordInfluence = wordInfluences[word][0] / wordInfluences[word][1]
            wordScore = wordFrequency * wordInfluence
            totalWordFrequency += wordFrequency
            totalWordScore += wordScore
   return totalWordScore/totalWordFrequency


def getCoinScores():
   import json
   wordFrequencies = getWordFrequencies()
   coinScores = {}
   allCoinWords = {}
   coinWords = {}
   try:
      wordInfluences = json.loads(open("wordInfluences.json").read())
   except: wordInfluences = {}
   avgWordScore = getAvgWordScore(wordInfluences, wordFrequencies)
   
   for coin in wordFrequencies:
      totalPos = totalPosFreq = 0
      totalNeg = totalNegFreq = 0
      for word in wordFrequencies[coin]:
         if word in wordInfluences:
            wordInfluence = wordInfluences[word][0] / wordInfluences[word][1]
            wordScore = (wordInfluence + -avgWordScore) * wordFrequencies[coin][word]
            if coin not in allCoinWords: 
               allCoinWords[coin] = {}
            allCoinWords[coin][word] = wordScore
            if wordScore > 0:
               totalPos += wordScore
               totalPosFreq += wordFrequencies[coin][word]
            else:
               totalNeg += abs(wordScore)
               totalNegFreq += wordFrequencies[coin][word]
      posScore = totalPos/totalPosFreq if totalPosFreq > 0 else 1
      negScore = totalNeg/totalNegFreq if totalNegFreq > 0 else 1
      if not (posScore == 1 or negScore == 1):
         coinScores[coin] = posScore/negScore
         
   for coin in allCoinWords:
      sortedCoinWords = sorted(allCoinWords[coin].items(), key=lambda x: x[1])
      topTenGoodWords = sortedCoinWords[-10:]
      topTenBadWords = sortedCoinWords[:9]
      coinWords[coin] = {"bad":topTenBadWords, "good":topTenGoodWords}
      
   return [coinScores, coinWords]


def generateExcelFile():
   import csv
   import json
   keys = []
   try:
      historicalCoinScores = json.loads(open("historicalCoinScores.json").read())
   except:
      historicalCoinScores = []
   timedCoinScores = []
   for coinScores in historicalCoinScores:
	   coinScores["coinScores"]["time"] = coinScores["time"][1]
	   timedCoinScores.append(coinScores)
   toCSV = [coinScores["coinScores"] for coinScores in timedCoinScores]
   for coinScores in toCSV:
	   keys.extend(list(coinScores.keys()))
   keys = list(set(keys))
   with open('coinScoresExcel.csv', 'w') as output_file:
      dict_writer = csv.DictWriter(output_file, keys)
      dict_writer.writeheader()
      dict_writer.writerows(toCSV)
    
def generatePredictionChart():
   try:
      historicalCoinScores = json.loads(open("historicalCoinScores.json").read())
   except:
      historicalCoinScores = []
   
   
    
def updateFile(outputFile="historicalCoinScores.json"):
   import json
   import time
   generateExcelFile()
   timeUnix = time.time()
   coinScores, coinWords = getCoinScores()
   currentTime = time.strftime("%Z - %d/%m/%Y, %H:%M:%S", time.localtime(time.time()))
   try:
      oldCoinScores = json.loads(open(outputFile).read())
   except: oldCoinScores = []
   oldCoinScores.append({"time": [timeUnix, currentTime], "coinScores": coinScores, "coinWords": coinWords})
   with open(outputFile, "w") as coinScoresFile:
      coinScoresFile.write(json.dumps(oldCoinScores, indent=2))
   
   currentTime = time.strftime("%Z - %d/%m/%Y, %H:%M:%S", time.localtime(time.time()))
   print("Current time: " + currentTime)
   for coin in coinWords:
      print(coin + " goodWords: " + str(coinWords[coin]["good"]) + " badWords: " + str(coinWords[coin]["bad"]) + "\n\n")
   for coin in sorted(coinScores.items(), key=lambda x: x[1]):
      print(coin[0] + " " + str(coin[1]))


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
   #loop()
   updateFile(outputFile="testHistoricalCoinScores.json") #Debugging


#Made by Alexpimania 2017
