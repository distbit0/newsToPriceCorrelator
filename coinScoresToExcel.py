import csv
import json
keys = []
historicalCoinScores = json.loads(open("/home/ap/newsToPriceCorrelator-master/historicalCoinScores.json").read())
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
