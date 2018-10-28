# -*- coding: utf-8 -*-
"""
Created on Wed Aug  8 19:16:17 2018

@author: Rafa

Implementation of the Classification KNN algorithm to predict values futur values
of assets


"""
from sklearn.neighbors import KNeighborsRegressor
from sklearn import preprocessing
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cross_validation import cross_val_score

class KNNprediction(object):
    # data in form of a pandas Series
    # k = number of neighbours
    # weights = 'uniform', 'distance', 'user-defined function'
    def __init__(self, data, window = None, min_err = 0.008):
        self.data = data
        self.X_train = []
        self.X_test = np.empty((0))
        self.y_train = np.empty((0))
        self.k = 2
        self.weights = 'uniform'
        if(window == None):
            self.window = int(0.1*data.size)
        else:
            self.window = window
        self.min_err = min_err
    
    #Since data will come in a pandas dataframe we need to adapt data
    def adapt_data(self, step = 1):
        y_trn = []
        for i in range(self.data.size - self.window - step):
            self.X_train.append(self.data.iloc[i:i+self.window,].values)
            y_trn.append(self.data.iloc[i+self.window+step,])
        self.y_train = np.array(y_trn)
        self.X_test = self.data.iloc[-self.window:,].values
    
    
    #Procedure to normalize data
    def normalize_data(self, norm = 'MinMax'):
        if(norm == 'MinMax'):
            min_max_scaler = preprocessing.MinMaxScaler()
            self.X_train = min_max_scaler.fit_transform(self.X_train)
            self.X_test = min_max_scaler.fit_transform(self.X_test.reshape(-1,1))
    
    #Procedure to find the optimized number of neighbors k and weights of distance
    def optimize_knn(self):
        scores = None
        scores2 = None
        for k in range(1,int(0.2*self.window)):
            knn = KNeighborsRegressor(k, weights=self.weights )
            knn.fit(self.X_train, self.y_train)
            scores = -cross_val_score(knn, self.X_train, self.y_train, scoring='neg_mean_absolute_error', cv=int(0.2*self.window))
            if(scores.mean() < self.min_err):
                self.k = k
                knn = KNeighborsRegressor(k, weights='distance')
                knn.fit(self.X_train, self.y_train)
                scores2 = -cross_val_score(knn, self.X_train, self.y_train, scoring='neg_mean_absolute_error', cv=int(0.2*self.window))
                if(scores.mean() > scores2.mean()):
                    self.weights = 'distance'
                    break
                break
    
    #Procedure to predict value
    def predict(self, step = 1):
         self.adapt_data(step)
         self.normalize_data()
         self.optimize_knn()
         knn = KNeighborsRegressor(n_neighbors = self.k, weights = self.weights)
         knn.fit(self.X_train, self.y_train)
         y_pred = knn.predict(self.X_test.reshape(1,-1))
         return y_pred
        












# =============================================================================
# knnp = KNNprediction(df_eurusd, 10)
# knnp.adapt_data()   
# 
# 
# def adapt_data(data, window, step = 3):
#     X = []
#     y = [] 
#     for i in range(data.size - window - step):
#         X.append(data.iloc[i:i+window,].values)
#         y.append(data.iloc[i+window+step,])
#     return X, y
# 
# 
# #Normalization of trainingn and test data
# #We need to catch exceptions here
# def normalize_data(X, norm = 'MinMax'):
#     X_train_minmax = X
#     if(norm == 'MinMax'):
#         min_max_scaler = preprocessing.MinMaxScaler()
#         X_train_minmax = min_max_scaler.fit_transform(X)
#     return X_train_minmax
#     
# def knn_predict(X, y, k):
#     knn = KNeighborsRegressor(n_neighbors=k)
#     knn.fit(X,y)
#     y_pred = knn.predict(X)
#     return y_pred
# 
# #The error we are to tolerate represts, in some way, the risk we are taknen   
# def Knn_optimizer(X_train_norm, y_train, min_err): 
#     scores = None
#     opt_k = 2
#     scores2 = None
#     weights = 'uniform'
#     for k in range(1,30):
#         knn = KNeighborsRegressor(k, weights=weights )
#         knn.fit(X_train_norm, y_train)
#         scores = -cross_val_score(knn, X_train_norm, y_train, scoring='neg_mean_absolute_error', cv=10)
#         if(scores.mean() < min_err):
#             opt_k = k
#             knn = KNeighborsRegressor(k, weights='distance')
#             knn.fit(X_train_norm, y_train)
#             scores2 = -cross_val_score(knn, X_train_norm, y_train, scoring='neg_mean_absolute_error', cv=10)
#             if(scores.mean() > scores2.mean()):
#                 weights = 'distance'
#                 break
#             break
#     return opt_k, weights
#     
#                     
#         
#     
# 
# 
#     
#     
# for i, weights in enumerate(['uniform','distance']):
#    total_scores = []
#    slopes = []
#    for k in range(1,30):
#        knn = KNeighborsRegressor(k, weights=weights)
#        knn.fit(X_norm,y_train)
#        scores = -cross_val_score(knn, X_norm, y_train, scoring='neg_mean_absolute_error', cv=10)
#        total_scores.append(scores.mean())
#     
#    plt.plot(range(1,len(total_scores)+1), total_scores, marker='o', label=weights)
#    plt.ylabel('cv score')
#    plt.legend()
# 
# 
# 
# k = 3
# y_pred = knn_predict(X_norm, y, k)
# 
# xx = np.stack(i for i in range(len(y)))
# plt.figure()
# plt.scatter(xx, y_pred, c='k', label='prediction')
# plt.plot(xx, y, c='g', label='data')
# plt.axis('tight')
# plt.legend()
# plt.title('KNeighborsRegressor')
# 
#     
# =============================================================================
