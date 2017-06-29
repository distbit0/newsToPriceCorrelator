import wordInfluencePredictor
import time
coinScores, coinWords = wordInfluencePredictor.getCoinScores()
currentTime = time.strftime("%Z - %d/%m/%Y, %H:%M:%S", time.localtime(time.time()))
print("Current time: " + currentTime)
for coin in coinWords:
   print(coin + " goodWords: " + str(coinWords[coin]["good"]) + " badWords: " + str(coinWords[coin]["bad"]) + "\n\n")
for coin in sorted(coinScores.items(), key=lambda x: x[1]):
   print(coin[0] + " " + str(coin[1]))
