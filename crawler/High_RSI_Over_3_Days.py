#coding:utf8

#not real Wilder’s Smoothing, only estimate

import requests
import time
import csv
import os

STOCK_NUMBER_INDEX = 0
STOCK_NAME_INDEX = 1
CHANGE_STATE_INDEX = 9
CHANGE_VALUE_INDEX = 10
RSI_DAY = 5

OUTPUT_FILE = '../output/' + os.path.basename(__file__).replace('.py', '.csv')

datestrs = ['20190425', '20190426', '20190429', '20190430', '20190502', '20190503', '20190506']

changeList = {}

def calculateRSI(changes):
	result = []

	for index, change in enumerate(changes):
		if change[0] == 'X':
			changes[index] = '+' + change[1:len(change)]
	try:
		changes = list(map(lambda i: float(i), changes))
	except Exception as e:
		raise Exception(e)

	for startIndex in range (0, 3):
		positiveChanges = list(filter(lambda i: i >= 0, changes[startIndex:startIndex + RSI_DAY]))
		negativeChanges = list(map(lambda i: abs(i), list(filter(lambda i: i < 0, changes[startIndex:startIndex + RSI_DAY]))))

		rsi = sum(positiveChanges) / (sum(positiveChanges) + sum(negativeChanges)) * 100

		result.append(round(rsi, 2))
	
	return result

for datestr in datestrs:
	r = requests.post('http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + datestr + '&type=ALL')

	for stockInfo in r.text.split('\n'):

		if len(stockInfo.split('",')) == 17 and stockInfo[STOCK_NUMBER_INDEX] != '=':

			stockInfo = stockInfo.split('","')
			stockNumber = stockInfo[STOCK_NUMBER_INDEX].replace('"', '')

			if stockNumber not in changeList:
				changeList[stockNumber] = {}
				changeList[stockNumber]['stockName'] = stockInfo[STOCK_NAME_INDEX]
				changeList[stockNumber]['change'] = []

			changeList[stockNumber]['change'].append(stockInfo[CHANGE_STATE_INDEX]+stockInfo[CHANGE_VALUE_INDEX])
	
	time.sleep(1)


with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8-sig') as csvfile:

	writer = csv.writer(csvfile)
	writer.writerow(['證券代號', '證券名稱', 'RSI前天', 'RSI昨天', 'RSI今天'])

	for stockNumber in list(changeList.keys()):
		stockInfo = changeList[stockNumber]
		try:
			rsiList = calculateRSI(stockInfo['change'])

			if rsiList[0] >= 80 and rsiList[1] >= 80 and rsiList[2] >= 80:
				writer.writerow([stockNumber, stockInfo['stockName'], rsiList[0], rsiList[1], rsiList[2]])

		except Exception as e:
			print(e)


