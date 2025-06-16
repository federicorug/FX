from abc import ABC, abstractmethod
from DataHandle import Fx_data as fd
from QuantLib import *
import math
from scipy.stats import norm

class Derivative(ABC):
    def __init__(self):

        self.mkt = fd()
        self.vol_inter = self.mkt.vol_interpolator()
        self.estr_inter = self.mkt.interp_estr
        self.sofr_inter = self.mkt.interp_sofr

    @abstractmethod
    def contract(self):
        pass
   
    @abstractmethod
    def Premium_EUR(self):
        pass

class VanillaOption(Derivative):
    def __init__(self):
        
        super().__init__()
        self.ref = self.mkt.spot


    def contract(self, option_type, strike, maturity_date, N):

        self.N = N
        self.T  = (maturity_date - self.mkt.today).days / 360
        self.strike = strike
        self.option_type = option_type


    def Premium_EUR(self):

        sigma = self.vol_inter((self.T,self.strike))
        rd = self.sofr_inter(self.T)                  
        rf = self.estr_inter(self.T)  

        d1 = (math.log(self.ref / self.strike) + (rd - rf + 0.5 * sigma ** 2) * self.T) / (sigma * math.sqrt(self.T))
        d2 = d1 - sigma * math.sqrt(self.T)

        if self.option_type == 'call':
            price = self.ref * math.exp(-rf * self.T) * norm.cdf(d1) - self.strike * math.exp(-rd * self.T) * norm.cdf(d2)
        elif self.option_type == 'put':
            price = self.strike * math.exp(-rd * self.T) * norm.cdf(-d2) - self.ref * math.exp(-rf * self.T) * norm.cdf(-d1)

        usdxeur = price
        eurptg = usdxeur/self.strike

        return eurptg * self.N /self.ref