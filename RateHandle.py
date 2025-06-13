import pandas as pd
import numpy as np
from xbbg import blp, pipeline
import datetime as dt
import scipy.interpolate as interpolate
import matplotlib.pyplot as plt
import xlwings as xw
import scipy.optimize as opt
from QuantLib import *
from scipy.optimize import minimize
from scipy.stats import norm

class rate:

    def __init__(self):

        self.fields = ['Security_Name','mid','maturity']
        self.tick = ['1Z','2Z','A','B','C', 'D', 'E','F','G','J','K','1','2','3','4','5','7','10','20']
        self.calendar = UnitedStates(UnitedStates.NYSE)
        self.today = dt.date.today()

    def data_take(self, coin):

        if coin == 'EUR':
            ticker = 'EESWE'
        elif coin == 'USD':
            ticker = 'USOSFR'

        rate_tick = ['{}{} Index'.format(ticker,i) for i in self.tick]
        rate_curve = [blp.bdp(i, flds=['Security_Name', 'PX_LAST','maturity']) for i in rate_tick]
        self.rate_curve = pd.concat(rate_curve, axis=0)
        self.rate_mat = [ ((i - self.today).days)/360 for i in self.rate_curve['maturity'].values]


    def rate_interpolator(self, coin):

        self.data_take(coin)

        return interpolate.interp1d(self.rate_mat, self.rate_curve['px_last'].values, kind='linear', fill_value='extrapolate')










