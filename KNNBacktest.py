# -*- coding: utf-8 -*-
"""
Created on Sat Aug 11 16:56:30 2018

@author: Rafa
Script to backtest with KNN algorithm
"""

from __future__ import (absolute_import, division, print_function, unicode_literals)
import backtrader as bt
from oanda_interface import Oanda_interface as interface
import datetime
from KNNprediction import KNNprediction
import pandas as pd

# Create a Stratey
class KNNStrategy(bt.Strategy):
    
    params = (
       ('maperiod', 1),
       ('printlog',True),
       ('window', 15),
       ('tot_data', pd.DataFrame())
    )
    
    
    def log(self, txt, dt=None, doprint=False):
        ''' Logging function for this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        
        # To keep track of pending orders
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.mysell = False
        self.mybuy = False

        
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
                self.mybuy = True
                
            elif order.issell():
                self.log('SELL EXECUTED, Price: %.2f, Size: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.size,
                          order.executed.value,
                          order.executed.comm))
                self.mysell = True

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
        #First we have to wait for at least two windows of size
        if(len(self) >= int(2*self.params.window)):
            # Check if an order is pending ... if yes, we cannot send a 2nd one
            if self.order:
                return      
           # Check if we are in the market
            if not self.position:
                # Not yet ... we MIGHT BUY if ...
                # Not yet ... we MIGHT BUY if ...
                knn_object = KNNprediction(self.params.tot_data[:len(self)], self.params.window)
                prediction = float(knn_object.predict())
                if self.dataclose[0] < prediction:
                    # BUY, BUY, BUY!!! (with all possible default parameters)
                    self.log('BUY CREATE, %.2f' % self.dataclose[0])
                    # Keep track of the created order to avoid a 2nd order
                    self.order = self.buy()
                elif self.dataclose[0] > prediction:
                    # SELL, SELL, SELL!!! (with all possible default parameters)
                    self.log('SELL CREATE, %.2f' % self.dataclose[0])
                    # Keep track of the created order to avoid a 2nd order
                    self.order = self.sell()
            else:
                knn_object = KNNprediction(self.params.tot_data[:len(self)], self.params.window)
                prediction = float(knn_object.predict())
                # Already in the market ... we might sell
                if self.mybuy:
                    if self.dataclose[0] > prediction:
                        self.order = self.close()
                        self.mybuy = False
                
                if self.mysell:
                    if self.dataclose[0] < prediction:
                        self.order = self.close()
                        self.mysell = False
    
#    def stop(self):
#        self.log('(MA Period %2d) Ending Value %.2f' %
#                 (self.params.maperiod, self.broker.getvalue()), doprint=True)



if __name__ == '__main__':
    #Create from date and to date as well as setting start and end points 
    #where our backtesitin is going to start
    #Create a cerebro entity
    instruments_list = ["EUR_USD","AUD_USD"]
    from_date = '2018-01-01'
    to_date = datetime.datetime.now()
    to_date = to_date.strftime('%Y-%m-%d')
    granularity = 'D'
    window = 20
    connection = interface()
    df_trade = connection.get_instruments_all(instruments_list, from_date, granularity = granularity)

    cerebro = bt.Cerebro()
    # Add a strategy
    cerebro.addstrategy(KNNStrategy, window=window, tot_data=df_trade['EUR_USD'].close)
                
    data_tmp =  bt.feeds.PandasData(dataname=df_trade['EUR_USD'],  
                                    openinterest = None,
                                    fromdate=df_trade['EUR_USD'].index[0], 
                                    todate=df_trade['EUR_USD'].index[len(df_trade['EUR_USD'])-1],
                                    name = 'EUR_USD')
    cerebro.adddata(data_tmp)

    #To set the initial cash that we have
    cerebro.broker.setcash(100000.0)
    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=100)
    # Set the commission - 0.1% ... divide by 100 to remove the %
    #cerebro.broker.setcommission(commission=0.1)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.plot(style="line")

