from abc import ABC, abstractmethod
from DataHandle import Fx_data as fd
from QuantLib import *
import math
from scipy.stats import norm

class Derivative(ABC):
    def __init__(self):
        self.mkt = None

    def download_data(self):
        self.mkt = fd()
        self.mkt.volbuilding()

    @abstractmethod
    def contract(self):
        pass
   
    @abstractmethod
    def Premium_EUR(self):
        pass

    @abstractmethod
    def delta_EUR(self):
        pass

    @abstractmethod
    def gamma(self):
        pass

    @abstractmethod
    def vega(self):
        pass

    @abstractmethod
    def theta_EUR():
        pass

class Vanilla(Derivative):

    def contract(self, option_type, strike, maturity_date, N):

        self.ref = self.mkt.spot
        self.domestic_curve = self.mkt.estr.rate_curve
        self.foreign_curve = self.mkt.sofr.rate_curve
        self.vol_ts = self.mkt.vol_handle
        self.maturity_date = maturity_date
        self.N = N
        self.T  = (maturity_date - self.mkt.today).days / 360
        self.strike = strike
        self.option_type = option_type

        if self.option_type == 'call':
            self.option_type = Option.Call
        elif self.option_type == 'put':
            self.option_type = Option.Put

        payoff = PlainVanillaPayoff(self.option_type, self.strike)
        exercise = EuropeanExercise(Date(self.maturity_date.day, self.maturity_date.month, self.maturity_date.year))

        self.fx_option = VanillaOption(payoff, exercise)
        spot_handle = QuoteHandle(SimpleQuote(self.ref))
        gk_process = GarmanKohlagenProcess(spot_handle, self.domestic_curve, self.foreign_curve, self.vol_ts)
        engine = AnalyticEuropeanEngine(gk_process)
        self.fx_option.setPricingEngine(engine)

    def Premium_EUR(self):

        npv = self.fx_option.NPV()
        eurptg = npv/self.strike

        return eurptg * self.N /self.ref
    
    def delta_EUR(self):
        
        return self.fx_option.delta() * self.N / self.strike
    
    def gamma(self):

        return self.fx_option.gamma()

    def vega(self):

        return self.fx_option.vega()

    def theta_EUR(self):

        return self.fx_option.thetaPerDay()
    
class BarOption(Derivative):

    def contract(self, option_type, strike, BarrierType, barrier, maturity_date, N):

        self.ref = self.mkt.spot
        self.domestic_curve = self.mkt.estr.rate_curve
        self.foreign_curve = self.mkt.sofr.rate_curve
        self.vol_ts = self.mkt.vol_handle
        self.maturity_date = maturity_date
        self.N = N
        self.T  = (maturity_date - self.mkt.today).days / 360
        self.strike = strike
        self.option_type = option_type
        self.BarrierType = BarrierType
        self.Barrier = barrier  

        if self.option_type == 'call':
            self.option_type = Option.Call

            if self.BarrierType == 'knock-in':
                self.BarrierType = Barrier.UpIn
            elif self.BarrierType == 'knock-out':
                self.BarrierType = Barrier.UpOut

        elif self.option_type == 'put':
            self.option_type = Option.Put

            if self.BarrierType == 'knock-in':
                self.BarrierType = Barrier.DownIn
            elif self.BarrierType == 'knock-out':
                self.BarrierType = Barrier.DownOut

        spot_handle = QuoteHandle(SimpleQuote(self.ref))
        gk_process = GarmanKohlagenProcess(spot_handle, self.domestic_curve, self.foreign_curve, self.vol_ts)

        payoff = PlainVanillaPayoff(self.option_type, self.strike)
        self.fx_option = BarrierOption(
            self.BarrierType,   
            self.Barrier,
            0.0,
            payoff,
            EuropeanExercise(Date(self.maturity_date.day, self.maturity_date.month, self.maturity_date.year))
        )

        engine = AnalyticBarrierEngine(gk_process)
        self.fx_option.setPricingEngine(engine)
 

    def Premium_EUR(self):

        npv = self.fx_option.NPV()
        eurptg = npv/self.strike

        return eurptg * self.N /self.ref
    
    def delta_EUR(self):
        
        return self.fx_option.delta() * self.N / self.strike
    
    def gamma(self):

        return self.fx_option.gamma()

    def vega(self):

        return self.fx_option.vega()

    def theta_EUR(self):

        return self.fx_option.thetaPerDay()


  
class DigOption(Derivative):

    def contract(self, option_type, strike, maturity_date, N):

        self.ref = self.mkt.spot
        self.domestic_curve = self.mkt.estr.rate_curve
        self.foreign_curve = self.mkt.sofr.rate_curve
        self.vol_ts = self.mkt.vol_handle
        self.maturity_date = maturity_date
        self.N = N
        self.T  = (maturity_date - self.mkt.today).days / 360
        self.strike = strike
        self.option_type = option_type


        if self.option_type == 'call':
            self.option_type = Option.Call


        elif self.option_type == 'put':
            self.option_type = Option.Put


        # spot_handle = QuoteHandle(SimpleQuote(self.ref))
        # gk_process = GarmanKohlagenProcess(spot_handle, self.domestic_curve, self.foreign_curve, self.vol_ts)

        # payoff = PlainVanillaPayoff(self.option_type, self.strike)
        # self.fx_option = BarrierOption(
        #     self.BarrierType,   
        #     self.Barrier,
        #     0.0,
        #     payoff,
        #     EuropeanExercise(Date(self.maturity_date.day, self.maturity_date.month, self.maturity_date.year))
        # )

        # engine = AnalyticBarrierEngine(gk_process)
        # self.fx_option.setPricingEngine(engine)

        payoff = CashOrNothingPayoff(self.option_type, self.strike, self.N)
        exercise = EuropeanExercise(Date(self.maturity_date.day, self.maturity_date.month, self.maturity_date.year))

        self.fx_option = EuropeanOption(payoff, exercise)

        spot_handle = QuoteHandle(SimpleQuote(self.ref))

        bsm_process = GarmanKohlagenProcess(spot_handle, self.domestic_curve, self.foreign_curve, self.vol_ts)

        engine = AnalyticEuropeanEngine(bsm_process)
        self.fx_option.setPricingEngine(engine)
 

    def Premium_EUR(self):

        npv = self.fx_option.NPV()

        return npv/self.ref
    
    def delta_EUR(self):
        
        return self.fx_option.delta() * self.N / self.strike
    
    def gamma(self):

        return self.fx_option.gamma()

    def vega(self):

        return self.fx_option.vega()

    def theta_EUR(self):

        return self.fx_option.thetaPerDay()






