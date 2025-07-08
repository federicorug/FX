import pandas as pd
from xbbg import blp, pipeline
from QuantLib import *



class FXCurve:
    def __init__(self):

        self.ticker = 'EURUSD BGN Curncy'
        self.fields = ['Security_Name','mid']
        self.maturity = ['1W', '2W', '3W','1M', '2M', '3M', '6M', '9M', '12M', '2Y', '3Y', '4Y', '5Y', '7Y', '10Y']
        cal1 = TARGET()
        cal2 = UnitedStates(UnitedStates.NYSE)
        self.calendar =  JointCalendar(cal1, cal2)
        self.today = Date.todaysDate()
        self.day_count = Actual360()
        self.spot = blp.bdp(self.ticker, flds = self.fields)['mid'].values[0]


    def data_take(self):

        self.ticker_maturity = ['EUR{} Curncy'.format(i) for i in self.maturity]
        self.pts_data = [blp.bdp(i, flds= self.fields + ['maturity']) for i in self.ticker_maturity]
        self.pts_data = pd.concat(self.pts_data, axis=0)
        self.forward_rates = self.spot + self.pts_data['mid'].values/10000
        self.pillars = [Date(i.day, i.month, i.year) for i in self.pts_data['maturity']]       
        self.zerocurve = CubicZeroCurve(
            self.pillars,
            self.forward_rates,
            self.day_count,
            self.calendar )
        self.curve = YieldTermStructureHandle(self.zerocurve)
        self.curve.allowsExtrapolation


    def fwd_interpolator(self, day):  

        return self.curve.zeroRate(day, self.day_count, Continuous, Annual).rate()