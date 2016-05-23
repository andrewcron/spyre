# tested with python2.7 and 3.4
from spyre import server

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import json
from datetime import datetime
try:
	import urllib2
except ImportError:
	import urllib.request as urllib2

from plotly.offline import offline
import plotly.graph_objs as go

class StocksWithPlotly(server.App):
	title = "Historical Stock Prices"

	inputs = [{	"type":'dropdown',
				"label": 'Company', 
				"options" : [
					{"label": "Choose A Company", "value":"empty"},
					{"label": "Google", "value":"GOOG", "checked":True},
					{"label": "Yahoo", "value":"YHOO"},
					{"label": "Apple", "value":"AAPL"}],
				"key": 'ticker', 
				"action_id": "update_data",
				"linked_key":'custom_ticker',
				"linked_type":'text',
			},
			{	"type":'text',
				"label": 'or enter a ticker symbol', 
				"key": 'custom_ticker', 
				"action_id": "update_data",
				"linked_key":'ticker',
				"linked_type":'dropdown',
				"linked_value":'empty' }]

	controls = [{"type" : "hidden",
					"label" : "get historical stock prices",
					"id" : "update_data" 
				}]

	outputs = [{"type" : "plot",
					"id" : "plot",
					"control_id" : "update_data",
					"tab" : "Plot"},
				{"type" : "table",
					"id" : "table_id",
					"control_id" : "update_data",
					"tab" : "Table",
					"sortable":True},
				{"type" : "html",
					"id" : "html_id",
					"control_id" : "update_data",
					"tab" : "Plotly"}]

	tabs = ["Plot", "Table", "Plotly"]

	def getData(self, params):
		ticker = params['ticker']
		if ticker=='empty':
				ticker=params['custom_ticker']
		# make call to yahoo finance api to get historical stock data
		api_url = 'https://chartapi.finance.yahoo.com/instrument/1.0/{}/chartdata;type=quote;range=3m/json'.format(ticker)
		result = urllib2.urlopen(api_url).read()
		data = json.loads(result.decode('utf-8').replace('finance_charts_json_callback( ','')[:-1])  # strip away the javascript and load json
		self.company_name = data['meta']['Company-Name']
		df = pd.DataFrame.from_records(data['series'])
		df['Date'] = pd.to_datetime(df['Date'],format='%Y%m%d')
		return df

	def getPlot(self, params):
		df = self.getData(params)
		plt_obj = df.set_index('Date').drop(['volume'],axis=1).plot()
		plt_obj.set_ylabel("Price")
		plt_obj.set_title(self.company_name)
		fig = plt_obj.get_figure()
		return fig

	def getHTML(self,params):
		df = self.getData(params)  # get data
		## create plotly chart data
		data = [
			go.Scatter(
				x=df['Date'],
				y=df['close'],
				name='Close'
				),
			go.Scatter(
				x=df['Date'],
				y=df['high'],
				name='High'
				),
			go.Scatter(
				x=df['Date'],
				y=df['low'],
				name='Low'
				)
			]
		## create plotly layout
		layout = go.Layout(
			autosize=False,
			width=700, height=500,
			title='{} Price'.format(self.company_name)
			)
		## create the figure
		fig = go.Figure(data=data, layout=layout)
		## generate the html
		html = offline.plot(fig, show_link=False, output_type='div', include_plotlyjs=False)
		return html

	def getCustomJS(self):
		## bolt on plotly library
		return offline.get_plotlyjs()

if __name__ == '__main__':
	ml = StocksWithPlotly()
	ml.launch(port=9097)
