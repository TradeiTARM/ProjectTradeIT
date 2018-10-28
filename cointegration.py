# -*- coding: utf-8 -*-
"""
Created on Thu May 24 19:12:08 2018

@author: Alex and Rafa
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
import statsmodels.tsa.stattools as tsa


class Cointegration(object):
    
    def __init__(self, window, raw_data=None, price='', corr_threshold = 0.8):
        self.window = window
        if(price in ['open','high','low','close']):
            self.price = price
        else:
            self.price = 'close'
        self.corr_threshold = corr_threshold
        self.raw_data = raw_data
        self.data = pd.DataFrame()
        
    def adapt_data(self):
        for k in self.raw_data.keys():
            df_tmp = pd.DataFrame(self.raw_data[k][self.price])
            self.data = self.data.join(df_tmp, how='inner')
        self.data.columns = self.raw_data.keys()
        
        
    '''Method to check correlation
    input: close data of all assets
    ouput: vector of tuples with correlated variables'''
    def check_corr(self):
        pass
    
    '''Method to check cointegrated pairs
    intput: tuple with two assets
    output: dict wity indep. variable, dep.variable, b1 and the order '''
    def get_cointegrated(self, first_position, window):
        pass
    
    def is_cointegrated(self, spread=None):
        pass
    
    def reach_mean(self, spread=None):
        pass




#Adapt data for the class

def adapt_data(data):
    df_trade = pd.DataFrame()
    for i, k in enumerate(data.keys()):
        if(i == 0):
            df_trade = pd.DataFrame(data[k].close.rename(k))
        else:
            df_tmp = pd.DataFrame(data[k].close.rename(k))
            df_trade = df_trade.join(df_tmp, how='inner')
#    df_trade.columns = data.keys()
    return df_trade
        


def normalize_data(data):
    scaler = MinMaxScaler()
    data_norm = scaler.fit_transform(data)
    data_norm = pd.DataFrame(data_norm, columns = data_norm.columns, index = data_norm.index)
    return(data_norm)
    

def correlated_pairs(data, threshold):
    corr_pairs = []
    corr = abs(data.corr())
    corr = corr[corr >= threshold]
    for i in range(len(corr)):
        for j in range(i+1,len(corr)):
            if(not pd.isnull(corr.iloc[i,j])):
                tmp = (corr.columns[i],corr.columns[j])
                corr_pairs.append(tmp)
    return corr_pairs 

#x and y must be dataframes not numpy arrays
def get_linear_model(data, x, y, critical_value):
    lm = LinearRegression()
    model = lm.fit(x.values.reshape(-1,1), y.values)
    y_pred = model.intercept_ + model.coef_*x
    spread = y_pred - y
    pvalue = tsa.adfuller(spread)[1]
    if(pvalue <= critical_value):
        spread = spread.rename(y.name+"$"+x.name)
        return spread
    else:
        return
      
    






