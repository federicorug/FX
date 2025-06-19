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
        self.rate_curve.allowsExtrapolation


    def rate_interpolator(self, target_date):
        try:
            return self.rate_curve.zeroRate(target_date, Actual365Fixed(), Continuous, Annual).rate()
        except:
            return self.rate_curve.zeroRate(self.rate_curve.referenceDate(), Actual365Fixed(), Continuous, Annual).rate()


