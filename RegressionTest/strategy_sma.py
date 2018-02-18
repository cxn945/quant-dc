from pyalgotrade import broker
from pyalgotrade import strategy
from pyalgotrade.bar import Frequency
from pyalgotrade.barfeed.csvfeed import GenericBarFeed
from pyalgotrade.bitstamp import common
from pyalgotrade.stratanalyzer import returns
from pyalgotrade.technical import cross
from pyalgotrade.technical import ma


class F():
    def __str__(self):
        return 'btcusdt'

coin = F()

class floatBroker(broker.backtesting.Broker):
    def getInstrumentTraits(self, instrument):
        return common.BTCTraits()


class MyStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, brk):
        super(MyStrategy, self).__init__(feed, brk)
        self.__position = None
        self.__instrument = instrument
        # We'll use adjusted close values instead of regular close values.
        self.setUseAdjustedValues(True)
        self.__prices = feed[instrument].getPriceDataSeries()
        self.__sma = {}
        self.__sma[60] = ma.SMA(self.__prices, 60)
        self.__sma[30] = ma.SMA(self.__prices, 30)
        self.__sma[25] = ma.SMA(self.__prices, 25)
        self.__sma[20] = ma.SMA(self.__prices, 20)
        self.__sma[15] = ma.SMA(self.__prices, 15)
        self.__sma[10] = ma.SMA(self.__prices, 10)
        self.__sma[5] = ma.SMA(self.__prices, 5)

    def getSMA(self, period):
        return self.__sma[period]

    def onEnterOk(self, position):
        execInfo = position.getEntryOrder().getExecutionInfo()

        self.info("BUY at $%.4f %.4f %.4f" % (execInfo.getPrice(), execInfo.getQuantity(), self.getBroker().getCash()))

    def onEnterCanceled(self, position):
        self.__position = None

    def onExitOk(self, position):
        execInfo = position.getExitOrder().getExecutionInfo()
        self.info("SELL at $%.4f %.4f %.4f" % (execInfo.getPrice(), execInfo.getQuantity(), self.getBroker().getCash()))
        self.__position = None

    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
        self.__position.exitMarket()

    def onBars(self, bars):
        # Wait for enough bars to be available to calculate a SMA.
        if self.__sma[30][-1] is None:
            return

        bar = bars[self.__instrument]
        # If a position was not opened, check if we should enter a long position.
        if self.__position is None:
            if cross.cross_above(self.__sma[10], self.__sma[30]) > 0:
                mbroker = self.getBroker()
                shares = mbroker.getCash() / bar.getPrice() * 0.95
                print("buy%.2f in %.2f use %d" % (shares, bar.getPrice(), mbroker.getCash()))
                self.__position = self.enterLong(self.__instrument, shares, True)
        # Check if we have to exit the position.
        elif not self.__position.exitActive() and cross.cross_below(self.__sma[5], self.__sma[25]) > 0:
            self.__position.exitMarket()


def run_strategy():
    # Load the yahoo feed from the CSV file
    feed = GenericBarFeed(Frequency.DAY, None, None)
    feed.addBarsFromCSV(coin, "2000.csv")

    # commission
    broker_commission = broker.backtesting.TradePercentage(0.002)
    broker_brk = floatBroker(10000, feed, broker_commission)
    # Evaluate the strategy with the feed.
    myStrategy = MyStrategy(feed, coin, broker_brk)

    returnsAnalyzer = returns.Returns()
    myStrategy.attachAnalyzer(returnsAnalyzer)

    myStrategy.run()
    print("Final portfolio value: $%.2f %.2f %.2f" % (
    myStrategy.getBroker().getEquity(), myStrategy.getBroker().getCash(), myStrategy.getBroker().getShares(coin)))


    myStrategy.info("Final portfolio value: $%.2f" % myStrategy.getResult())










