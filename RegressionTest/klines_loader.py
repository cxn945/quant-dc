import pandas as pd
import time
import config

from hbsdk import ApiClient

API_KEY = "API_KEY"
API_SECRET = "API_SECRET"

headList=["Date Time","Open","High","Low","Close","Volume","Adj Close"]

client = ApiClient(API_KEY, API_SECRET)
file_path = "2000.csv"

# load history of k-line
def load_kline(period = config.DEFAULT_PREIOD, symbol = config.DEFAULT_PREIOD):

    print "start load data, symbol:%s, period: %s minutes" % (symbol, period)
    history = client.mget('/market/history/kline', symbol=symbol, period='%dmin' % period, size=2000)
    print "total raw data count: %d" % len(history)
    jdict= reduce(redf, history, [])
    print "total data of reduce count: %d" % len(history)
    df = pd.DataFrame.from_dict(jdict)
    df.to_csv(generate_file_path(period, symbol), index=False, header=headList)

def dtf(x):
    time_local = time.localtime(x)
    return time.strftime("%Y-%m-%d %H:%M:%S",time_local)

def rf(x):
    return [dtf(x.id), x.open, x.high, x.low, x.close, x.vol, x.close]

def redf(x,y):
    return x+[rf(y)]

def generate_file_path(period, symbol):
    global file_path
    file_path = "data/history-%s-%smin.csv"%(symbol, period)
    return file_path

def get_file_path():
    return file_path
