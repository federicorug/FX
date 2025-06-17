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

# class rate:

#     def __init__(self):

#         self.fields = ['Security_Name','mid','maturity']
#         self.tick = ['1Z','2Z','A','B','C', 'D', 'E','F','G','J','K','1','2','3','4','5','7','10','20']
#         self.calendar = UnitedStates(UnitedStates.NYSE)
#         self.today = dt.date.today()

#     def data_take(self, coin):

#         if coin == 'EUR':
#             ticker = 'EESWE'
#         elif coin == 'USD':
#             ticker = 'USOSFR'

#         rate_tick = ['{}{} Index'.format(ticker,i) for i in self.tick]
#         rate_curve = [blp.bdp(i, flds=['Security_Name', 'PX_LAST','maturity']) for i in rate_tick]
#         self.rate_curve = pd.concat(rate_curve, axis=0)
#         self.rate_mat = [ ((i - self.today).days)/360 for i in self.rate_curve['maturity'].values]


#     def rate_interpolator(self, coin):

#         self.data_take(coin)

#         return interpolate.interp1d(self.rate_mat, self.rate_curve['px_last'].values, kind='linear', fill_value='extrapolate')




class rate:

    def __init__(self):

        self.fields = ['Security_Name','mid','maturity']
        self.tick = ['1Z','2Z','A','B','C', 'D', 'E','F','G','J','K','1','2','3','4','5','7','10','20']
        self.today = dt.date.today()
        self.ql_today = Date(self.today.day, self.today.month, self.today.year)
        Settings.instance().evaluationDate = self.ql_today
        self.day_count = Actual360()

    def data_take(self, coin):

        if coin == 'EUR':
            ticker = 'EESWE'
            self.calendar = TARGET()
        elif coin == 'USD':
            ticker = 'USOSFR'
            self.calendar = UnitedStates(UnitedStates.NYSE)

        rate_tick = ['{}{} Index'.format(ticker,i) for i in self.tick]
        rate_curve = [blp.bdp(i, flds=['Security_Name', 'PX_LAST','maturity']) for i in rate_tick]
        self.rate_curve = pd.concat(rate_curve, axis=0)

        ql_date = [Date(i.day, i.month, i.year) for i in self.rate_curve['maturity']]
        rates = self.rate_curve['px_last'].values/100
        self.discount_curve = ZeroCurve(ql_date, rates, self.day_count, self.calendar)
        self.rate_curve = YieldTermStructureHandle(self.discount_curve)


    def rate_interpolator(self):

        pillar_dates = [self.calendar.advance(self.ql_today, Period(i, Months)) for i in range(1, 150, 3)]
        pillar_rates = [self.rate_curve.zeroRate(d, self.day_count, Continuous).rate() for d in pillar_dates]
        pillar_mat = [self.day_count.yearFraction(self.ql_today, i) for i in pillar_dates]


        return interpolate.interp1d(pillar_mat, pillar_rates, kind='linear', fill_value='extrapolate')




