period = 1 * 86400


##########Utility Functions#############
def removeText(text, term="https?://[^\s]+"):
   import re
   term = "(?P<text>" + term + ")"
   while True:
      textToRemove = re.search(term, text)
      if textToRemove:
         text = text.replace(textToRemove.group("text"), "").replace("  ", " ") 
      else: break
   return text
  
  
def chunks(listToCut, maxLength):
   for i in range(0, len(listToCut), maxLength):
      yield listToCut[i:i+maxLength]


def initTwitterApi():
   import tweepy
   twitterKeys = open("twitterKeysMiner.txt").read().strip().split()
   auth = tweepy.OAuthHandler(twitterKeys[0], twitterKeys[1])
   auth.set_access_token(twitterKeys[2], twitterKeys[3])
   return tweepy.API(auth, wait_on_rate_limit_notify=True, wait_on_rate_limit=True)


def getTwitterPosts(coinNames, period):
   import tweepy
   import time
   from datetime import datetime
   import string
   tweets = {}
   
   coinNames = [key for key in coinNames.keys()]
   api = initTwitterApi()
   sinceDate = datetime.fromtimestamp(time.time() - period).strftime('%Y-%m-%d')
   for chunk in chunks(coinNames, 10):
      for tweet in tweepy.Cursor(api.search, q=" OR ".join(chunk), tweet_mode="extended", since=sinceDate, lang="en").items(1000):
         tweetText = removeText(tweet._json["full_text"]).lower().strip()
         translator = str.maketrans('', '', string.punctuation)
         tweetText = tweetText.translate(translator)
         tweets[tweetText] = tweet._json["user"]["id"]
   return tweets
   
   
def removeDuplicateWords(coinPosts):
   import itertools
   allCoinWords = []
   for user in coinPosts:
      userWords = []
      for post in coinPosts[user]: 
         userWords.extend(post.split(" "))
      allCoinWords.extend(list(set(userWords)))
   return allCoinWords
   
   
def generateAndRemoveDuplicateBigrams(coinPosts):
   bigrams = []
   for user in coinPosts:
      userBigrams = []
      for post in coinPosts[user]:
         userBigrams.extend([b[0] + " " + b[1] for b in zip(post.split(" ")[:-1], post.split(" ")[1:])])
      bigrams.extend(list(set(userBigrams)))
   return bigrams
   
   
def getDelayTime():
   import time
   secondsPerDay = 60*60*24
   currentTime = time.time()
   secondsSinceMidnight = currentTime % secondsPerDay
   secondsUntilMidnight = secondsPerDay - secondsSinceMidnight
   return 0#secondsUntilMidnight
   
   
def logError(error):
   import json
   import time
   currentTime = time.strftime("%Z - %d/%m/%Y, %H:%M:%S", time.localtime(time.time()))
   errorLogs = json.loads(open("errorLogs.txt").read())
   errorLogs.append({"time": currentTime, "error": error})
   with open("errorLogs.json", "w+") as errorLogFile:
      errorLogFile.write(json.dumps(errorLogs))
########################################


def getCoinNames():
   from poloniex import Poloniex
   polo = Poloniex()
   coinMarketList = [market[market.index("_") + 1:] for market in polo.return24hVolume().keys() if "BTC_" in market]
   coinList = polo.returnCurrencies()
   coinNames = {}
   ignoredCoins = ["burst", "clams", "counterparty", "expanse", "dash", "horizon", "magi", "nem", "nexium", "nxt", "omni", "radium", "ripple", "shadow", "stellar", "tether"]
   for coin in coinList:
      if not coinList[coin]["name"].lower() in ignoredCoins and coin in coinMarketList:
         coinNames[coinList[coin]["name"].lower()] = "BTC_" + coin.upper()
   return coinNames


def amalgamatePosts(coinNames, period):
   posts = {}
   posts.update(getTwitterPosts(coinNames, period))
   return posts


def categorizePosts(posts, coinNames):
   import json
   categorizedPosts = {}
   for post in posts:
      coins = [coinName for coinName in coinNames if coinName in post]
      if len(coins) == 1:
         coin = coins[0]
         if not coin in categorizedPosts.keys():
            categorizedPosts[coin] = {}
         if not posts[post] in categorizedPosts[coin]:
            categorizedPosts[coin][posts[post]] = []
         categorizedPosts[coin][posts[post]].append(post)
   return categorizedPosts
 

def getWordFrequency(categorizedPosts):
   from nltk import FreqDist
   wordFrequencies = {}
   for coin in categorizedPosts:
      wordFrequencies[coin] = {}
      bigrams = generateAndRemoveDuplicateBigrams(categorizedPosts[coin])
      allWords = removeDuplicateWords(categorizedPosts[coin])
      allWords.extend(bigrams)
      wordOccurences = FreqDist(allWords).most_common()
      totalWordCount = len(allWords)
      for word in wordOccurences:
         wordCountRatio = (word[1] / totalWordCount) * 100
         wordFrequencies[coin][word[0]] = wordCountRatio
   return wordFrequencies
   
   
def getCoinScores(wordFrequencies):
   import json
   coinScores = {}
   wordInfluences = json.loads(open("wordInfluences.json").read())
   avgWordScore = sum([value[0] / value[1] for value in wordInfluences.values()]) / float(len(wordInfluences))
   
   for coin in wordFrequencies:
      coinScore = 0
      validWords = 0
      for word in wordFrequencies[coin]:
         if word in wordInfluences:
            coinScore += (wordInfluences[word][0] / wordInfluences[word][1]) * wordFrequencies[coin][word]
            validWords += wordFrequencies[coin][word]
      if validWords != 0:
         coinScore = coinScore/validWords
         coinScores[coin] = coinScore
   return [avgWordScore, coinScores]
   
   
def saveCoinScores(coinScores):
   import json
   import time
   timeUnix = time.time()
   currentTime = time.strftime("%Z - %d/%m/%Y, %H:%M:%S", time.localtime(time.time()))
   oldCoinScores = json.loads(open("historicalCoinScores.json").read())
   oldCoinScores.append({"time": [timeUnix, currentTime], "avgWordScore": coinScores[0], "coinScores": coinScores[1]})
   with open("historicalCoinScores.json", "w") as coinScoresFile:
      coinScoresFile.write(json.dumps(oldCoinScores))
   print(coinScores)
   
   
import time
import sys
import traceback
while True:
   time.sleep(getDelayTime())
   while True:
      try:
   coinNames = getCoinNames()
   posts = amalgamatePosts(coinNames, period)
   categorizedPosts = categorizePosts(posts, coinNames)
   wordFrequencies = getWordFrequency(categorizedPosts)
   coinScores = getCoinScores(wordFrequencies)
   saveCoinScores(coinScores)    
         break
      except:
         print("Exception occured: \n\n" + traceback.format_exc())
         logError(traceback.format_exc())
         continue
