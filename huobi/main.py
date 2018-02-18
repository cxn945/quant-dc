from pyalgotrade import strategy
from pyalgotrade.bar import Frequency
from pyalgotrade.technical import cross
from pyalgotrade.technical import ma

from hbClient import hbCoinType
from hbClient import hbTradeClient as hbClient
from liveApi.livebarfeed import LiveFeed
from liveApi.livebroker import LiveBroker

COIN_TYPE=hbCoinType('iost', 'usdt')
K_PERIOD=15
REQ_DELAY = 0

#COIN_TYPE='ltc'

class MyStrategy(strategy.BaseStrategy):
    def __init__(self, feed, instrument, brk):
        super(MyStrategy, self).__init__(feed, brk)
        self.__position = None
        self.__instrument = instrument
        # We'll use adjusted close values instead of regular close values.
        self.__prices = feed[instrument].getPriceDataSeries()
        self.__sma = {}
        self.__sma[60] = ma.SMA(self.__prices, 60)
        self.__sma[10] = ma.SMA(self.__prices, 10)
        self.__sma[30] = ma.SMA(self.__prices, 30)
        self.__sma[25] = ma.SMA(self.__prices, 25)
        self.__sma[5] = ma.SMA(self.__prices, 5)

    def getSMA(self, period):
        return self.__sma[period]
    
    def onEnterOk(self, position):
        execInfo = position.getEntryOrder().getExecutionInfo()
        self.info("BUY at $%.4f %.4f" % (execInfo.getPrice(), execInfo.getQuantity()))

    def onEnterCanceled(self, position):
        self.__position = None

    def onExitOk(self, position):
        execInfo = position.getExitOrder().getExecutionInfo()
        self.info("SELL at $%.4" % (execInfo.getPrice()))
        self.__position = None

    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
        self.__position.exitMarket()

    def onBars(self, bars):
        # Wait for enough bars to be available to calculate a SMA.
        bar = bars[self.__instrument]
        if self.getFeed().isHistory():
            return
        if self.__sma[60][-1] is None:
            return
        print("onBars %s:%s: close:%.4f"%(self.__instrument, bar.getDateTimeLocal(), bar.getPrice()))

        bar = bars[self.__instrument]
                    
        # If a position was not opened, check if we should enter a long position.
        if self.__position is None:
            if cross.cross_above(self.__sma[10], self.__sma[30]) > 0:
                mbroker = self.getBroker()
                shares = mbroker.getCash()/bar.getPrice()*0.95
                self.__position = self.enterLongLimit(self.__instrument, bar.getPrice(), shares, True)
        # Check if we have to exit the position.
        elif not self.__position.exitActive() and cross.cross_below(self.__sma[5], self.__sma[25]) > 0:
            self.__position.exitLimit(bar.getPrice())


def run_strategy():
    # Load the yahoo feed from the CSV file
    feed = LiveFeed([COIN_TYPE], Frequency.MINUTE*K_PERIOD, REQ_DELAY)

    # commission
#    broker_commission = broker.backtesting.TradePercentage(0.002)
#    broker_brk = broker.backtesting.Broker(20000, feed, broker_commission)
    liveBroker = LiveBroker(COIN_TYPE, hbClient(COIN_TYPE))
    # Evaluate the strategy with the feed.
    myStrategy = MyStrategy(feed, COIN_TYPE, liveBroker)
    
#    returnsAnalyzer = returns.Returns()
#    myStrategy.attachAnalyzer(returnsAnalyzer)
    

    # Attach the plotter to the strategy.
#    plt = plotter.StrategyPlotter(myStrategy)
    # Include the SMA in the instrument's subplot to get it displayed along with the closing prices.
#    plt.getInstrumentSubplot("orcl").addDataSeries("SMA60", myStrategy.getSMA(60))
#    plt.getInstrumentSubplot("orcl").addDataSeries("SMA10", myStrategy.getSMA(10))
#    plt.getInstrumentSubplot("orcl").addDataSeries("SMA30", myStrategy.getSMA(30))
    # Plot the simple returns on each bar.
#    plt.getOrCreateSubplot("returns").addDataSeries("Simple returns", returnsAnalyzer.getReturns())
    
    
    myStrategy.run()
#    print "Final portfolio value: $%.2f" % myStrategy.getBroker().getEquity()
    print "Final portfolio value: $%.4f" % myStrategy.getBroker().getCash()
#    myStrategy.info("Final portfolio value: $%.2f" % myStrategy.getResult())

    # Plot the strategy.
#    plt.plot()

run_strategy()















