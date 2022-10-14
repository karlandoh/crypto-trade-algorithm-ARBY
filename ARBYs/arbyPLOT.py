#!/usr/local/bin/python3
from arbyGOODIE import *

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn import linear_model, datasets
import datetime

class data():
	def __init__(self):
		self.plot(init=True)

	def regression(self,amount):
		self.plot(init=True)
		return str(datetime.datetime.fromtimestamp((amount-self.y_value)/self.slope_value))

	def plot(self,name=None,init=None):
		df = pd.read_excel(open(f"{os.getcwd()}/SoldierInfo_plot.xls", 'rb'), sheet_name='balances')

		df['Timestamp'] = pd.to_datetime(df['Timestamp'])

		X = np.array([x.timestamp() for x in df['Timestamp']]).reshape(-1,1)
		
		y = df['Total (F)']

		lm = linear_model.LinearRegression()
		model = lm.fit(X,y)
		line = lm.predict(X)

		df['Regression'] = line

		slope = lm.coef_[0]
		y_intercept = lm.intercept_

		if y_intercept < 0:
			sign = '-'
		else:
			sign = '+'

		equation = f"y={slope}x {sign} {abs(y_intercept)}"

		ax = plt.gca()
		ax.set_title(equation)
		df.plot(kind='line',x='Timestamp',y='Available',color='green',ax=ax)
		df.plot(kind='line',x='Timestamp',y='Total (S)',color='yellow',ax=ax)
		df.plot(kind='line',x='Timestamp',y='Total (F)',color='red',ax=ax)
		df.plot(kind='line',x='Timestamp', y='Regression',color='black',ax=ax)

		self.slope_value = slope
		self.y_value = y_intercept

		print({'slope': slope, 'y_intercept': y_intercept})
		
		if init != None:
			plt.close()
			return None

		if name == None:
			plt.savefig(f'''{os.getcwd()}/plots/{datetime.datetime.today().strftime("%b %d %Y %I:%M:%S %p")}.png''')
		else:
			plt.savefig(f'''{os.getcwd()}/plots/{name}.png''')
		
		plt.close()



		return {'slope': slope, 'y_intercept': y_intercept}

if __name__ == '__main__':
	plot = data()