import pandas as pd
import numpy as np
from xbbg import blp, pipeline
import datetime as dt
import scipy.interpolate as interpolate
from QuantLib import *
from scipy.optimize import minimize
from scipy.stats import norm
from RateHandle import RateCurve 
from FXHandle import FXCurve
import matplotlib.pyplot as plt


class VolSurface:
    def __init__(self): 
        
        self.maturity = ['ON','1W', '2W', '3W','1M', '2M', '3M', '6M', '9M', '1Y', '2Y', '3Y', '4Y', '5Y', '7Y', '10Y']
        self.isin = ['EURUSDV','EURUSD35R','EURUSD25R','EURUSD15R','EURUSD10R','EURUSD5R','EURUSD5B','EURUSD10B','EURUSD15B','EURUSD25B','EURUSD35B']
        self.mkt_vola_struct = []
        self.call_put_ticker = ['','Call35', 'Call25','Call15','Call10','Call5','Put5','Put10','Put15','Put25','Put35']
        self.flds = ['Security_Name', 'mid','maturity']
        self.surf = pd.DataFrame(index = self.maturity, columns = self.isin)
        self.deltas = [0,0.35,0.25,0.15,0.10,0.05]

        for j, isi in enumerate(self.isin):
            self.surf['{}'.format(self.isin[j])] = pd.concat([blp.bdp('{}{} Curncy'.format(isi,i) , flds=self.flds) 
                        for i in self.maturity], axis=0).values

        for i in range(1, len(self.call_put_ticker) // 2 + 1):
            self.surf[self.call_put_ticker[i]] = self.surf[self.isin[0]] + self.surf[self.isin[-i]] + .5 * self.surf[self.isin[i]]
            self.surf[self.call_put_ticker[-i]] =  self.surf[self.isin[0]] + self.surf[self.isin[-i]] - .5 * self.surf[self.isin[i]]
            

    def building(self):

        self.estr = RateCurve()
        self.sofr = RateCurve()
        self.estr.data_take('EUR')
        self.sofr.data_take('USD')
        self.fx = FXCurve()
        self.fx.data_take()

        def strike_from_delta_forward(F, T, sigma , delta,  option_type='call'):

            sigma = sigma * 0.01   

            if option_type == 'call':
                
                d1 = np.array([norm.ppf(delta * np.exp(self.estr.rate_interpolator(i) * self.fx.day_count.yearFraction(self.fx.today,i))) if self.fx.day_count.yearFraction(self.fx.today,i) < 1 else norm.ppf(delta) for i in T])
               
            else:
                delta = delta + 1
                d1 = np.array([norm.ppf(delta * np.exp(self.estr.rate_interpolator(i) * self.fx.day_count.yearFraction(self.fx.today,i))) if self.fx.day_count.yearFraction(self.fx.today,i) < 1 else norm.ppf(delta) for i in T])
            
            tau = np.array([self.fx.day_count.yearFraction(self.fx.today,i) for i in T])
            K = self.fx.spot / np.exp(d1 * sigma * np.sqrt(tau) - (self.sofr.rate_interpolator(T)- self.estr.rate_interpolator(T) + 0.5 * sigma**2 )* tau) 

            return K
        
        self.atm_strikes = np.insert(self.fx.forward_rates, 0 , self.fx.spot)
        self.pillars = [self.fx.calendar.advance(self.fx.today, 1, Days)]  + self.fx.pillars
        self.strike_surface = pd.DataFrame(index = self.maturity, columns=self.call_put_ticker[1:])
        self.strike_surface['ATM'] = self.atm_strikes

        for i in range(1, len(self.call_put_ticker) // 2 + 1):

            self.strike_surface[self.call_put_ticker[i]] = strike_from_delta_forward(self.fx.forward_rates, self.pillars, self.surf[self.call_put_ticker[i]].values, self.deltas[i],  option_type='call')
            self.strike_surface[self.call_put_ticker[-i]] = strike_from_delta_forward(self.fx.forward_rates, self.pillars, self.surf[self.call_put_ticker[-i]].values, -self.deltas[i],  option_type='put')

        self.strike_surface = self.strike_surface[['Put5','Put10','Put15','Put25','Put35','ATM','Call35','Call25','Call15','Call10','Call5']]
        self.moneyness = np.linspace(0.75, 1.25, 50) * self.fx.spot
        self.volatility_matrix = np.zeros([len(self.pillars), len(self.moneyness)])
        
        for i in range(len(self.pillars)):

            strikes = list(self.strike_surface.iloc[i,:].values)
            fwd = self.atm_strikes[i]
            expiryTime = self.fx.day_count.yearFraction(self.fx.today,self.pillars[i])
            marketVols = list(self.surf[['Put5','Put10','Put15','Put25','Put35','EURUSDV','Call35','Call25','Call15','Call10','Call5']].iloc[i,:].values/100)
          
            beta = 0.5
            sabr = SABRInterpolation(
                strikes,
                marketVols,
                expiryTime,
                fwd,
                alpha=0.2,   
                beta=beta,
                nu=0.3,      
                rho=0.0,     
                alphaIsFixed=False,
                betaIsFixed=True,  
                nuIsFixed=False,
                rhoIsFixed=False
            )

            # print('T {}:'.format(expiryTime),"Alpha =", sabr.alpha(), "Beta  =", "Nu    =", sabr.nu(),"Rho   =", sabr.rho())
            # plt.plot(strikes, [sabr(strike) for strike in strikes], label='sabr interpolation')
            # plt.title('{}'.format(expiryTime))
            # plt.plot(strikes, marketVols, label='market')
            # plt.plot(strikes, [sabrVolatility(strike, fwd, expiryTime, sabr.alpha() ,sabr.beta(), sabr.nu(), sabr.rho()) for strike in strikes], label='sabr model')
            # plt.legend()
            # plt.show()

            self.volatility_matrix[i,:] = np.array([sabrVolatility(strike, fwd, expiryTime, sabr.alpha() ,sabr.beta(), sabr.nu(), sabr.rho())for strike in self.moneyness])

        self.zerosurface = BlackVarianceSurface(
                                                    self.fx.today,               
                                                    self.fx.calendar,            
                                                    self.pillars,       
                                                    self.moneyness,             
                                                    self.volatility_matrix.T.tolist(),                
                                                    Actual360()           
                                                )
        self.volatility_matrix = pd.DataFrame(self.volatility_matrix, columns=self.moneyness, index=self.pillars)
        self.volatility_matrix.index.name = 'maturity'
        self.volatility_matrix.columns.name = 'moneyness'
        self.surface = BlackVolTermStructureHandle(self.zerosurface)
