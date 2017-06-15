def generateGraph():
	import matplotlib.pyplot as plt
	result = {'apr': 13, 'jun': 13, 'jul': 13, 'aug': 13}
	plt.plot(list(result.values()), label="1")
	plt.ylabel('Number')
	plt.xlabel('Time (Months)')
	plt.title('Number per month')
	plt.xticks(range(len(result)), result.keys())
	plt.legend()
	plt.savefig("ff.png")
   
def generateCoinWordsText():
   pass
   
def sendEmails():
   import smtplib
   smtpobj = smtplib.SMTP_SSL('smtp.gmail.com', 465)
   smtpobj.login("snazzyemailsender@gmail.com", "wsxcdeWSXCDE99!wsxcdeWSXCDE99!")
   smtpobj.sendmail("snazzyemailsender@gmail.com", "brainpasf@gmail", "Subject:jdjdjd\n\n\n\n fhrfrrgruyfgrydjssjgd")


import csv
reader = csv.DictReader(open('coinScoresExcel.csv'))

result = {}
for row in reader:
    key = row.pop('time')
    result[key] = row
    
print(result)
