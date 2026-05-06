pip install -U lib-pybroker

import os
from pyboroker import alpaca

#setting app Alpaca with a secure autentication using enviroment stored variables

alpaca = Alpaca(os.environ['ALPACA_API_KEY'], os.environ['ALPACA_SECRET_KEY'])

#The main comand we'll use is Alpaca.query
##EXAMPLE##
#Suppose we want to download 1 year of 1 minute data for AAPL:

tickers=['AAPL']
data_1m = alpaca.query(
    tickers=tickers,
    start_date="2025-01-01",
    end_date="2025-12-31",
    time_frame="1m"
)
