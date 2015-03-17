import requests
import pandas as pd
import pandas.io.data as web
from bs4 import BeautifulSoup

def GetSP500List():
	'''Download the list of S&P 500 companies from wikipedia
	returns list of companies'''
	data = []

	wiki_sp500 = 'http://en.wikipedia.org/wiki/List_of_S%26P_500_companies'

	r = requests.get(wiki_sp500)
	assert(r.ok)
	soup = BeautifulSoup(r.text)

	table = soup.find('table')

	for line in table.findAll('tr'):
		temp_line = line.findAll('td')
		if(temp_line != []):
			d = {}
			temp_symbol = temp_line[0].getText()
			
			# Need to replace period with dash for future use in yahoo
			if(temp_symbol.find('.') != -1):
				temp_symbol = temp_symbol.replace('.','-')

			d['Symbol'] = temp_symbol
			d['Company'] = temp_line[1].getText()
			d['Sector'] = temp_line[3].getText()
			d['Subsector'] = temp_line[4].getText()
			data.append(d)

	df = pd.DataFrame(data)
	# df.to_csv('SP500.csv',index=False)
	return df

def GetSP500Data(filename):
	'''Download stock information on S&P 500 stocks
	Gets names of S&P companies from file in filename
	returns end-of-day prices and volume'''

	SP500_names = pd.read_csv(filename)

	all_data = {}
	for ticker in SP500_names['Symbol']:
		print ticker
		all_data[ticker] = web.get_data_yahoo(ticker,'1/1/2000','3/13/2015')

	SP500price = pd.DataFrame({tic: data['Adj Close']
							for tic, data in all_data.iteritems()})
	SP500volume = pd.DataFrame({tic: data['Volume']
							 for tic, data in all_data.iteritems()})

	# SP500price.to_csv('SP500price.csv')
	# SP500volume.to_csv('SP500volume.csv')
	return SP500price,SP500volume

def GetSP500Options(filename):
	'''Download options chain data for S&P 500 stocks
	load S&P stock names from filename
	return data frame with options information'''
	sp500 = pd.read_csv(filename)
	Options = pd.DataFrame()

	for ticker in sp500['Symbol']:

		print ticker
		call_options,put_options = GetOptionsChain(ticker)
		if(len(call_options)!=0):
			call_options['Symbol'] = ticker
			call_options['Call/Put'] = 'Call'
			call_options = call_options.set_index(['Symbol','Call/Put','Strike'])
		if(len(put_options)!=0):
			put_options['Symbol'] = ticker
			put_options['Call/Put'] = 'Put'
			put_options = put_options.set_index(['Symbol','Call/Put','Strike'])

		Options = Options.append(call_options)
		Options = Options.append(put_options)

	return Options

def GetOptionsChain(ticker):
	'''Takes a ticker symbol and returns
	call options chain and
	put options chain'''

	stock_link = 'https://finance.yahoo.com/q/op?s=' + ticker + '+Options'
	r = requests.get(stock_link)
	assert(r.ok)
	soup = BeautifulSoup(r.text)

	table = soup.findAll('table')

	if(len(table) == 3):
		calls_df = ExtractTable(table[1]) #Calls table is table[1]
		puts_df = ExtractTable(table[2]) #Puts table is table[2]
	else:
		calls_df = pd.DataFrame()
		puts_df = pd.DataFrame()

	return calls_df,puts_df

def ExtractTable(table):
	'''Extract information from yahoo options chain table'''
	data = []
	for line in table.findAll('tr'):
		temp_line = line.findAll('td')

		if(len(temp_line) == 10):
			# Number of columns in yahoo options chain table = 10
			d = {}
			d['Strike'] = float(temp_line[0].getText())
			d['Last'] = float(temp_line[2].getText())
			d['Bid'] = float(temp_line[3].getText())
			d['Ask'] = float(temp_line[4].getText())
			d['Change'] = float(temp_line[5].getText())
			# d['PercentChange'] = temp_line[6].getText()
			d['PercentChange'] = float(temp_line[6].getText()[:-2])
			d['Volume'] = float(temp_line[7].getText())
			d['OpenInterest'] = float(temp_line[8].getText())
			d['ImpliedVolatility'] = float(temp_line[9].getText()[:-2])
			data.append(d)

	df = pd.DataFrame(data)
	# df = df.set_index(df['Strike'])
	# df = df.set_index(['Strike'])
		
	return df