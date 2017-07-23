def removeText(text, term="https?://[^\s]+"):
   import re
   term = "(?P<text>" + term + ")"
   while True:
      textToRemove = re.search(term, text)
      if textToRemove:
         text = text.replace(textToRemove.group("text"), "").replace("  ", " ") 
      else: break
   return text
   

def removeStopWords(wordsList):
   config = getConfig()
   if type(wordsList) == list:
      wordsList = [word for word in wordsList if not (word.replace("'", "") in config["stopWords"] or set([word.replace("'", "") for part in word]) < set(config["stopWords"]))]
      return wordsList
         
   if type(wordsList) == dict:
      editedWordList = {}
      for word in wordsList:
         if word.replace("'", "") in config["stopWords"]:
            pass
         elif set([word.replace("'", "") for part in word]) < set(config["stopWords"]):
            pass
         else:
            editedWordList[word] = wordsList[word]
      return editedWordList
   
   
def removeDuplicateWords(coinPosts):
   allCoinWords = []
   for user in coinPosts:
      userWords = []
      for post in coinPosts[user]: 
         userWords.extend(post.split(" "))
      allCoinWords.extend(list(set(userWords)))
   allCoinWords = removeStopWords(allCoinWords)
   return allCoinWords
   

def generateAndRemoveDuplicateNgrams(coinPosts):
   import nltk
   ngrams = []
   config = getConfig()
   for user in coinPosts:
      userNgrams = []
      for post in coinPosts[user]:
         userNgrams.extend([" ".join(list(ngram)) for ngram in nltk.ngrams(post.split(), 2)])
         userNgrams.extend([" ".join(list(ngram)) for ngram in nltk.ngrams(post.split(), 3)])
      ngrams.extend(list(set(userNgrams)))
   ngrams = [ngram for ngram in ngrams if not ([word.replace("'", "") for word in ngram] < config["stopWords"])]
   return ngrams
   
   
def sleepForPeriod(delay=0):
   import time
   config = getConfig()
   period = config["period"]
   currentTime = time.time() - delay
   time.sleep(period - currentTime % period)
   
   
def logError():
   import json
   import time
   import traceback
   error = traceback.format_exc()
   print("Exception occured: \n\n" + traceback.format_exc())
   currentTime = time.strftime("%Z - %d/%m/%Y, %H:%M:%S", time.localtime(time.time()))
   try:
      errorLogs = json.loads(open("errorLogs.json").read())
   except: errorLogs = []
   errorLogs.append({"time": currentTime, "error": error})
   with open("errorLogs.json", "w") as errorLogFile:
      errorLogFile.write(json.dumps(errorLogs, indent=2, sort_keys=True))
   time.sleep(300)
   
   
def getConfig():
   import json
   config = json.loads(open("config.json").read())
   return config
   
   
def getCoinNames():
   from poloniex import Poloniex
   polo = Poloniex()
   config = getConfig()
   coinMarketList = [market[market.index("_") + 1:] for market in polo.return24hVolume().keys() if "BTC_" in market]
   coinList = polo.returnCurrencies()
   coinNames = {}
   ignoredCoins = config["ignoredCoins"]
   for coin in coinList:
      if not coinList[coin]["name"].lower() in ignoredCoins and coin in coinMarketList:
         coinNames[coinList[coin]["name"].lower()] = "BTC_" + coin.upper()
   return coinNames
   
   
def initTwitterApi(function):
   config = getConfig()
   import tweepy
   twitterKeys = config["twitterKeys" + function]
   auth = tweepy.OAuthHandler(twitterKeys[0], twitterKeys[1])
   auth.set_access_token(twitterKeys[2], twitterKeys[3])
   return tweepy.API(auth, wait_on_rate_limit_notify=True, wait_on_rate_limit=True)
   
   
def amalgamatePosts():
   posts = {}
   coinNames = getCoinNames()
   posts.update(getTwitterPosts())
   return posts
   
   
def categorizePosts():
   import json
   posts = amalgamatePosts()
   coinNames = getCoinNames()
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
   
   
def getWordFrequencies():
   from nltk import FreqDist
   wordFrequencies = {}
   categorizedPosts = categorizePosts()
   for coin in categorizedPosts:
      wordFrequencies[coin] = {}
      ngrams = generateAndRemoveDuplicateNgrams(categorizedPosts[coin])
      allWords = removeDuplicateWords(categorizedPosts[coin])
      allWords.extend(ngrams)
      wordOccurences = FreqDist(allWords).most_common()
      totalWordCount = len(allWords)
      for word in wordOccurences:
         wordFrequencies[coin][word[0]] = word[1] / totalWordCount
   return wordFrequencies
