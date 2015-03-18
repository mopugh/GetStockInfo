import StockInfo
reload(StockInfo)
import pandas as pd

datadir = 'DataFiles/'
read_filename = datadir + 'SP500.csv'
SP500_names = pd.read_csv(read_filename)
# Change filename to date
write_filename = '03172015.csv'
write_filename = datadir + write_filename

TotalOptionsChain = StockInfo.GetSP500Options(read_filename)
TotalOptionsChain.to_csv(write_filename)