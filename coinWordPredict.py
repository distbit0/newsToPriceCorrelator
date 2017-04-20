period = 1 * 86400


##########Utility Functions#############
def removeLink(text):
   import re
   while True:
      link = re.search("(?P<url>https?://[^\s]+)", text)
      if link:
         text = text.replace(link.group("url"), "").replace("  ", " ") 
      else: break
   return text
  
  
def chunks(listToCut, maxLength):
    for i in range(0, len(listToCut), maxLength):
        yield listToCut[i:i+maxLength]
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


def getTwitterTweets(coinNames, period):
   import tweepy
   import time
   from datetime import datetime
   import string
   tweets = []
   usersTweets = {}
   
   coinNames = [key for key in coinNames.keys()]
   twitterKeys = open("twitterKeys.txt").read().strip().split() 
   auth = tweepy.OAuthHandler(twitterKeys[0], twitterKeys[1])
   auth.set_access_token(twitterKeys[2], twitterKeys[3])
   api = tweepy.API(auth, wait_on_rate_limit_notify=True, wait_on_rate_limit=True)
   
   sinceDate = datetime.fromtimestamp(time.time() - period * 2).strftime('%Y-%m-%d')
   untilDate = datetime.fromtimestamp(time.time() - period).strftime('%Y-%m-%d')
   for chunk in chunks(coinNames, 10):
      for tweet in tweepy.Cursor(api.search, q=" OR ".join(chunk), tweet_mode="extended", since=sinceDate, until=untilDate, lang="en").items(1000):
         tweetText = removeLink(tweet._json["full_text"]).lower()
         if not tweet._json["user"]["id"] in usersTweets.keys():
            usersTweets[tweet._json["user"]["id"]] = []
         if not tweetText in usersTweets[tweet._json["user"]["id"]]:
            translator = str.maketrans('', '', string.punctuation)
            tweets.append(tweetText.translate(translator))
            usersTweets[tweet._json["user"]["id"]].append(tweetText.translate(translator))
   return tweets


def categorizePosts(posts, coinNames, period):
   import json
   coinPosts = {}
   for post in posts:
      coins = [coinName for coinName in coinNames if coinName in post]
      if len(coins) == 1:
         coin = coins[0]
         post = post.replace(coin, "")
         if not coin in coinPosts.keys():
            coinPosts[coin] = "" 
         coinPosts[coin] += post + " "
   return coinPosts
 

def getWordFrequency(coinPosts):
   import string
   from nltk import FreqDist
   coinWordCountRatios = {}
   for coin in coinPosts:
      coinWordCountRatios[coin] = {}
      wordFrequencies = FreqDist(list(coinPosts[coin])).most_common()
      bigrams = [b[0] + " " + b[1] for b in zip(coinPosts[coin].split(" ")[:-1], coinPosts[coin].split(" ")[1:])]
      wordFrequencies.extend(FreqDist(bigrams).most_common())
      totalWordCount = len(coinPosts[coin].split())
      for word in wordFrequencies:
         wordCountRatio = (word[1] / totalWordCount) * 100
         coinWordCountRatios[coin][word[0]] = wordCountRatio
   return coinWordCountRatios
   

def getPriceMovement(coinNames, period):
   import time
   from poloniex import Poloniex
   polo = Poloniex()
   coinPriceChanges = {}
   for coin in coinNames:
      startTime = time.time() - period
      coinWtdAvg = polo.returnChartData(coinNames[coin], start=startTime)[0]["weightedAverage"]
      lastCoinWtdAvg = polo.returnChartData(coinNames[coin], start=startTime - period, end=startTime)[0]["weightedAverage"]
      changePercent = ((coinWtdAvg / lastCoinWtdAvg) * 100) - 100
      coinPriceChanges[coin] = changePercent  
   return coinPriceChanges


def getWordsInfluence(coinPriceChanges, coinWordCountRatios):
   wordInfluences = {}
   for coin in coinWordCountRatios:
      for word in coinWordCountRatios[coin].keys():
         if not word in wordInfluences.keys():
            wordInfluences[word] = [0, 0]
         incrementCount = wordInfluences[word][1]
         totalInfluence = wordInfluences[word][0]
         wordInfluences[word] = [totalInfluence + coinWordCountRatios[coin][word], incrementCount + 1]
   return wordInfluences
   
   
def updateFile(wordInfluences):
   import json
   wordInfluencesFile = json.loads(open("wordInfluences.txt").read())
   for word in wordInfluences:
      if not word in wordInfluencesFile:
         wordInfluencesFile[word] = [0, 0]
      incrementCount = wordInfluencesFile[word][1]
      totalInfluence = wordInfluencesFile[word][0]
      wordInfluencesFile[word] = [totalInfluence + wordInfluences[word][0], incrementCount + wordInfluences[word][1]]
   with open("wordInfluences.txt", "w") as wordInfluencesFileObj:
      wordInfluencesFileObj.write(json.dumps(wordInfluencesFile))
      
while True:
   import time
   try:
      coinNames = getCoinNames()
      tweets = getTwitterTweets(coinNames, period)
      coinPosts = categorizePosts(tweets, coinNames, period)
      coinWordCountRatios = getWordFrequency(coinPosts)
      coinPriceChanges = getPriceMovement(coinNames, period)
      wordInfluences = getWordsInfluence(coinPriceChanges, coinWordCountRatios)
      updateFile(wordInfluences)
   except:
      pass
   time.sleep(period)
