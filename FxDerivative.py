from abc import ABC, abstractmethod
from DataHandle import Fx_data as fd
from QuantLib import *
import math
from scipy.stats import norm

class Derivative(ABC):
    def __init__(self):

        self.mkt = fd()
        self.mkt.volbuilding()

    @abstractmethod
    def contract(self):
        pass
   
    @abstractmethod
    def Premium_EUR(self):
        pass

class Vanilla(Derivative):
    def __init__(self):
        
        super().__init__()
        self.ref = self.mkt.spot


    def contract(self, option_type, strike, maturity_date, N):

        self.maturity_date = maturity_date
        self.N = N
        self.T  = (maturity_date - self.mkt.today).days / 360
        self.strike = strike
        self.option_type = option_type


    def Premium_EUR(self):

        domestic_curve = self.mkt.estr.rate_curve
        foreign_curve = self.mkt.sofr.rate_curve
        vol_ts = self.mkt.vol_handle
        
        if self.option_type == 'call':
            option_type = Option.Call
        elif self.option_type == 'put':
            option_type = Option.Put

        payoff = PlainVanillaPayoff(option_type, self.strike)
        exercise = EuropeanExercise(Date(self.maturity_date.day, self.maturity_date.month, self.maturity_date.year))

        fx_option = VanillaOption(payoff, exercise)

        spot_handle = QuoteHandle(SimpleQuote(self.ref))

        gk_process = GarmanKohlagenProcess(spot_handle, domestic_curve, foreign_curve,  vol_ts)
        engine = AnalyticEuropeanEngine(gk_process)
        fx_option.setPricingEngine(engine)
        npv = fx_option.NPV()

        eurptg = npv/self.strike

        return eurptg * self.N /self.ref





