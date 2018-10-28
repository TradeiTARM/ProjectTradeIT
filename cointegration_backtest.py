# -*- coding: utf-8 -*-
"""
Created on Thu Aug 23 15:57:26 2018

@author: Rafa
"""

from __future__ import (absolute_import, division, print_function, unicode_literals)
import backtrader as bt
from oanda_interface import Oanda_interface as interface
import datetime
import cointegration

class TestStrategy(bt.Strategy):
    
    params = (
       ('maperiod', 5),
       ('printlog',True)
    )
    
    
    def log(self, txt, dt=None, doprint=False):
        ''' Logging function for this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        self.dataclose_2 = self.datas[1].close
        # To keep track of pending orders
        self.order = None
        self.buyprice = None
        self.buycomm = None
        # Add a MovingAverageSimple indicator
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.maperiod)
         # Indicators for the plotting show
#        bt.indicators.ExponentialMovingAverage(self.datas[0], period=25)
#        bt.indicators.WeightedMovingAverage(self.datas[0], period=25,
#                                            subplot=True)
#        bt.indicators.StochasticSlow(self.datas[0])
#        bt.indicators.MACDHisto(self.datas[0])
#        rsi = bt.indicators.RSI(self.datas[0])
#        bt.indicators.SmoothedMovingAverage(rsi, period=10)
#        bt.indicators.ATR(self.datas[0], plot=False)
        
############ NOTIFY ORDER ####################################################        
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return
        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Size: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.size,
                     order.executed.value,
                     order.executed.comm))
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
                
            elif order.issell():
                self.log('SELL EXECUTED, Price: %.2f, Size: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.size,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        # Write down: no pending order
        self.order = None
    
############ NOTITY_TRADE #####################################################
    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))    
        
########### NEXT ##############################################################        
    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.4f' % self.dataclose[0])
        self.log('Close, %.4f' % self.dataclose_2[0])
        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return      
       # Check if we are in the market
        if not self.position:
            # Not yet ... we MIGHT BUY if ...
            # Not yet ... we MIGHT BUY if ...
            if self.dataclose[0] > self.sma[0]:
                # BUY, BUY, BUY!!! (with all possible default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()
        else:
            # Already in the market ... we might sell
            if self.dataclose[0] < self.sma[0]:
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()
    
#    def stop(self):
#        self.log('(MA Period %2d) Ending Value %.2f' %
#                 (self.params.maperiod, self.broker.getvalue()), doprint=True)



if __name__ == '__main__':
    #Create from date and to date as well as setting start and end points 
    #where our backtesitin is going to start
    #Create a cerebro entity
    instruments_list = ["EUR_USD","USD_JPY","GBP_USD","USD_CAD","USD_CHF","AUD_USD","NZD_USD","EUR_GBP","EUR_CHF",
                        "EUR_CAD","EUR_AUD","EUR_NZD","EUR_JPY","GBP_JPY","CHF_JPY","CAD_JPY","AUD_JPY","NZD_JPY",                
                        "GBP_CHF","GBP_AUD","GBP_CAD"]
    from_date = '2018-01-01'
    to_date = datetime.datetime.now()
    to_date = to_date.strftime('%Y-%m-%d')
    granularity = 'D'
    window = 10
    connection = interface()
    df_trade = connection.get_instruments_all(instruments_list, from_date, granularity = granularity)

    cerebro = bt.Cerebro()
    # Add a strategy
    cerebro.addstrategy(TestStrategy)
            
    

     for i in df_trade.keys():
         data_tmp =  bt.feeds.PandasData(dataname=df_trade[i].iloc[window:,],  
                                openinterest = None,
                                fromdate=df_trade[i].iloc[window:,].index[0], 
                                todate=df_trade[i].index[len(df_trade[i])-1],
                                name = i)
         cerebro.adddata(data_tmp)

    #To set the initial cash that we have
    cerebro.broker.setcash(1000000.0)
    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)
    #Set the commission - 0.1% ... divide by 100 to remove the %
    cerebro.broker.setcommission(commission=0.1)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.plot(style="line")