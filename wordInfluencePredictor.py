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
   twitterKeys = open("twitterKeysPredictor.txt").read().strip().split() 
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
   usersPosts = {}
   finalPosts = []

   posts.update(getTwitterPosts(coinNames, period))

   for post in posts:
      if not posts[post] in usersPosts.keys():
         usersPosts[posts[post]] = []
      if not post in usersPosts[posts[post]]:
         finalPosts.append(post)
         usersPosts[posts[post]].append(post)
   return finalPosts


def categorizePosts(posts, coinNames):
   import json
   categorizedPosts = {}
   for post in posts:
      coins = [coinName for coinName in coinNames if coinName in post]
      if len(coins) == 1:
         coin = coins[0]
         post = removeText(post, coin)
         if not coin in categorizedPosts.keys():
            categorizedPosts[coin] = "" 
         categorizedPosts[coin] += post + " "
   return categorizedPosts
 

def getWordFrequency(catgeorizedPosts):
   import string
   from nltk import FreqDist
   wordFrequencies = {}
   for coin in catgeorizedPosts:
      wordFrequencies[coin] = {}
      wordOccurences = FreqDist(catgeorizedPosts[coin].split()).most_common()
      bigrams = [b[0] + " " + b[1] for b in zip(catgeorizedPosts[coin].split(" ")[:-1], catgeorizedPosts[coin].split(" ")[1:])]
      wordOccurences.extend(FreqDist(bigrams).most_common())
      totalWordCount = len(catgeorizedPosts[coin].split())
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
            coinScore += wordInfluences[word][0] / wordInfluences[word][1]
            validWords += 1
      coinScore = coinScore/validWords
      coinScores[coin] = coinScore
   return [avgWordScore, coinScores]
   
def saveCoinScores(coinScores):
   print(coinScores)
   
coinNames = getCoinNames()
posts = amalgamatePosts(coinNames, period)
categorizedPosts = categorizePosts(posts, coinNames)
wordFrequencies = getWordFrequency(categorizedPosts)
coinScores = getCoinScores(wordFrequencies)
saveCoinScores(coinScores) #[1]
