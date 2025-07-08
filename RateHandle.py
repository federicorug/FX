import pandas as pd
from xbbg import blp, pipeline
from QuantLib import *




class RateCurve:

    def __init__(self):

        self.fields = ['Security_Name','mid','maturity']
        self.maturity_ticker = ['1Z','2Z','A','B','C', 'D', 'E','F','G','J','K','1','2','3','4','5','7','10','20']
        self.today = Date.todaysDate()
        Settings.instance().evaluationDate = self.today
        self.day_count = Actual360()

    def data_take(self, coin):

        if coin == 'EUR':
            underlying_ticker = 'EESWE'
            self.calendar = TARGET()
        elif coin == 'USD':
            underlying_ticker = 'USOSFR'
            self.calendar = UnitedStates(UnitedStates.NYSE)

        curve_ticker = ['{}{} Index'.format(underlying_ticker,i) for i in self.maturity_ticker]
        curve_data = [blp.bdp(i, flds=['Security_Name', 'PX_LAST','maturity']) for i in curve_ticker]
        self.curve_data = pd.concat(curve_data, axis=0)
        pillars = [Date(i.day, i.month, i.year) for i in self.curve_data['maturity']]
        rates = self.curve_data['px_last'].values/100
        self.zero_curve = ZeroCurve(pillars, rates, self.day_count, self.calendar)
        self.curve = YieldTermStructureHandle(self.zero_curve)
        self.curve.allowsExtrapolation


    def rate_interpolator(self, target_date):
        try:
            return self.curve.zeroRate(target_date, self.day_count, Continuous, Annual).rate()
        except:
            return self.curve.zeroRate(self.curve.referenceDate(), self.day_count, Continuous, Annual).rate()


