# -*- coding: utf-8 -*-
"""
Created on Tue May  8 20:06:49 2018

@author: Rafa
"""
import oandapyV20
import oandapyV20.endpoints.instruments as instruments
import pandas as pd
import numpy as np
import datetime
import oandapyV20.endpoints.orders as orders


class Oanda_interface(object):
    
    def __init__(self):
        self.__token = "8a28831dadfaf585b668399a4b6a8487-9cd75a7d7417679dae686ca812fc73a7"
        self.__accountId = '101-004-6106396-001'
        
    '''Gets the json object in data frame
     @price = c/l/o/h
     @trade = ask/bid/mid
    '''
     #Get only one column with one valo 'open', 'close', 'high' or 'low' and the instrument  
    def get_trade_df(self,  instrument, data, price='c', trade='bid'):
        candles = pd.DataFrame.from_dict(data)
        df_trade = pd.DataFrame(columns=['time', instrument])
        for i in range(len(candles)):
            temp_dict = {}
            temp_data = pd.DataFrame.from_dict(candles.loc[i,'candles'])
            temp_data = temp_data.loc[price]
            time = temp_data.loc['time']
            value = float(temp_data.loc[trade])
            temp_dict['time'] = time
            temp_dict[instrument] = value
            df_trade = df_trade.append(temp_dict, ignore_index=True)
        df_trade = df_trade.set_index('time')
        df_trade.index = pd.to_datetime(df_trade.index)
        return(df_trade)
       
    #Execute an order in the broker     
    def new_order(self, instrument, units):
        order = {}
        data = {}
        order["timeInForce"] = "FOK"
        order["instrument"] = instrument,
        order["units"] = units,
        order["type"] = "MARKET",
        order["positionFill"] = "DEFAULT"
        data ['order'] = order
        client = oandapyV20.API(access_token=self.__token)
        r = orders.OrderCreate(self.__accountId, data=data) 
        client.request(r)
        print(r.response)     
            
     
    def get_instruments(self, instruments_list, from_date, to_date = '', granularity = "D", price = "MBA"):
        df = pd.DataFrame()
        params = {}
        params['granularity'] = granularity
        params['price'] = price
        if from_date != '':
            params['from'] = from_date
        if to_date !='':
            params['to'] = to_date
        else:
            now = datetime.datetime.now()
            now = now.strftime('%Y-%m-%d')
            params['to'] = now
           
        client = oandapyV20.API(access_token=self.__token)
        
        for i in range(len(instruments_list)):
            try:
                r = instruments.InstrumentsCandles(instrument = instruments_list[i], params = params)
                json_response = client.request(r)
                data = pd.DataFrame.from_dict(json_response)
                if df.empty:
                    df = self.get_trade_df(instrument = instruments_list[i], data = data)
                else:
                    df = df.join(self.get_trade_df(instrument = instruments_list[i], data = data), how="inner")
            except:
                continue
        return(df)
        
        
    #Get a list of instruments with all data including 'open', 'high' 'low', 'close' and 'volume' values 
    def get_instruments_all(self, instruments_list, from_date, to_date = '', granularity = "D", price = "MBA"):
        data = {}
        params = {}
        params['granularity'] = granularity
        params['price'] = price
        if from_date != '':
            params['from'] = from_date
        if to_date !='':
            params['to'] = to_date
        else:
            now = datetime.datetime.now()
            now = now.strftime('%Y-%m-%d')
            params['to'] = now
           
        client = oandapyV20.API(access_token=self.__token)
        
        for i in range(len(instruments_list)):
            try:
                r = instruments.InstrumentsCandles(instrument = instruments_list[i], params = params)
                json_response = client.request(r)
                data[instruments_list[i]] = self.get_tot_trade(json_response)
            except:
                continue
        return(data)
        
    #Get total trade with open, close, high, low and volume indicators  
    def get_tot_trade(self, data, trade='bid'):
        temp_dict = {}
        candles = pd.DataFrame.from_dict(data)
        df_trade = pd.DataFrame(columns=['Date', 'open', 'high', 'low', 'close', 'volume'])
        for i in range(len(candles)):
            temp_dict['Date'] = candles.loc[i,'candles']['time']
            temp_dict['open'] = float(candles.loc[i,'candles'][trade]['o'])
            temp_dict['high'] = float(candles.loc[i,'candles'][trade]['h'])
            temp_dict['low'] = float(candles.loc[i,'candles'][trade]['l'])
            temp_dict['close'] = float(candles.loc[i,'candles'][trade]['c'])
            temp_dict['volume'] = int(candles.loc[i,'candles']['volume'])
            df_trade = df_trade.append(temp_dict, ignore_index=True)
        df_trade = df_trade.set_index('Date')
        df_trade.index = pd.to_datetime(df_trade.index)
        return(df_trade)
        
        
        
        
        
        