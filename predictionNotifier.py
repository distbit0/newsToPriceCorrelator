def getChartData():
	import csv
	reader = csv.DictReader(open('coinScoresExcel.csv'))
	result = {}
	for row in reader:
		key = row.pop('time')
		result[key] = row
	return result
		
		
def generateGraph():
	getChartData
	import matplotlib.pyplot as plt
	chartData = getChartData()
	plt.plot(list(chartData.values()), label="1")
	plt.ylabel('Number')
	plt.xlabel('Time (Days)')
	plt.title('Cryptocurrency predictions')
	plt.xticks(range(len(chartData)), chartData.keys())
	plt.legend()
	plt.savefig("ff.png")
   
def generateCoinWordsText():
   pass
   
def sendEmails():
	import smtplib
	smtpobj = smtplib.SMTP_SSL('smtp.gmail.com', 465)
	smtpobj.login("snazzyemailsender@gmail.com", "wsxcdeWSXCDE99!wsxcdeWSXCDE99!")
	smtpobj.sendmail("snazzyemailsender@gmail.com", "brainpasf@gmail", "Subject:jdjdjd\n\n\n\n fhrfrrgruyfgrydjssjgd")
