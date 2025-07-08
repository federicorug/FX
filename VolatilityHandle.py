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




class VolSurface:
    def __init__(self): 
        
        self.maturity = ['ON','1W', '2W', '3W','1M', '2M', '3M', '6M', '9M', '1Y', '2Y', '3Y', '4Y', '5Y', '7Y', '10Y']

        atmvol = []
        rrvol25 = []
        rrvol10 = []    
        bfvol25 = []
        bfvol10 = []

        for i in self.maturity:
            
            atmvol += [blp.bdp('EURUSDV{} Curncy'.format(i) , flds=['Security_Name', 'mid','maturity'])]
            rrvol25 += [blp.bdp('EURUSD25R{} Curncy'.format(i), flds=['Security_Name', 'mid','maturity'])]
            rrvol10 += [blp.bdp('EURUSD10R{} Curncy'.format(i)  , flds=['Security_Name', 'mid','maturity'])]
            bfvol25 += [blp.bdp('EURUSD25B{} Curncy'.format(i), flds=['Security_Name', 'mid','maturity'])]
            bfvol10 += [blp.bdp('EURUSD10B{} Curncy'.format(i), flds=['Security_Name', 'mid','maturity'])]

        atmvol = pd.concat(atmvol, axis=0)
        rrvol25 = pd.concat(rrvol25, axis=0)
        rrvol10 = pd.concat(rrvol10, axis=0)
        bfvol25 = pd.concat(bfvol25, axis=0)
        bfvol10 = pd.concat(bfvol10, axis=0)

        self.surf = pd.DataFrame(np.array([atmvol['mid'].values,
                     rrvol10['mid'].values,
                     rrvol25['mid'].values,
                     bfvol10['mid'].values,
                     bfvol25['mid'].values,
                     ]).T,  self.maturity, columns=['ATM','RR10','RR25','BF10','BF25'])
        
        self.surf['Call25'] = self.surf['ATM'] + self.surf['BF25'] + .5 * self.surf['RR25']
        self.surf['Call10'] = self.surf['ATM'] + self.surf['BF10'] + .5 * self.surf['RR10']
        self.surf['Put25'] = self.surf['ATM'] + self.surf['BF25'] - .5 * self.surf['RR25']
        self.surf['Put10'] = self.surf['ATM'] + self.surf['BF10'] - .5 * self.surf['RR10']


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

                d1 = np.array([norm.ppf(delta * np.exp(self.sofr.rate_interpolator(i) * self.fx.day_count.yearFraction(self.fx.today,i))) if self.fx.day_count.yearFraction(self.fx.today,i) < 1 else norm.ppf(delta) for i in T])

            else:
                delta = delta + 1

                d1 = np.array([norm.ppf(delta * np.exp(self.sofr.rate_interpolator(i) * self.fx.day_count.yearFraction(self.fx.today,i))) if self.fx.day_count.yearFraction(self.fx.today,i) < 1 else norm.ppf(delta) for i in T])
            
            tau = np.array([self.fx.day_count.yearFraction(self.fx.today,i) for i in T])

            K = self.atm_strikes * np.exp(-d1 * sigma * np.sqrt(tau) + 0.5 * sigma**2 * tau)
            return K
        
        self.atm_strikes = np.insert(self.fx.forward_rates, 0 , self.fx.spot)
        self.pillars = [self.fx.calendar.advance(self.fx.today, 1, Days)]  + self.fx.pillars
        self.K_call25 = strike_from_delta_forward(self.fx.forward_rates, self.pillars, self.surf['Call25'].values, 0.25,  option_type='call')
        self.K_call10 = strike_from_delta_forward(self.fx.forward_rates, self.pillars, self.surf['Call10'].values, 0.10,  option_type='call')
        self.K_Put25 = strike_from_delta_forward(self.fx.forward_rates, self.pillars, self.surf['Put25'].values,-0.25,  option_type='put')
        self.K_Put10 = strike_from_delta_forward(self.fx.forward_rates, self.pillars, self.surf['Put10'].values, -0.10, option_type='put')

        self.strike_surface = pd.DataFrame(np.array([ self.K_Put10, self.K_Put25, self.atm_strikes , self.K_call25, self.K_call10]).T, self.maturity, columns=['put10','put25','atm','call25','call10'])

        self.moneyness = np.linspace(0.75, 1.25, 50) * self.fx.spot
        self.volatility_matrix = np.zeros([len(self.K_Put10), len(self.moneyness)])
        cons=(
        {'type': 'ineq', 'fun': lambda x:  0.99 - x[1]},
        {'type': 'ineq', 'fun': lambda x: x[1]},    
        {'type': 'ineq', 'fun': lambda x: x[3]}
        )
        bnds = ((1e-6, 5.0), (0.0, 1.0),(1e-6, 5.0), (-0.999, 0.999))

        def f(params):
            vols = np.array([
                sabrVolatility(strike, fwd, expiryTime, *params)
                for strike in strikes
            ])*100
            err = ((vols - np.array(marketVols))**2 ).mean() **.5
            return err
        
        for i in range(len(self.K_Put10)):

            params = [0.1] * 4
            strikes = self.strike_surface.iloc[i,:].values
            fwd = self.atm_strikes[i]
            expiryTime = self.fx.day_count.yearFraction(self.fx.today,self.pillars[i])
            marketVols = self.surf[['Put10','Put25','ATM','Call25','Call10']].iloc[i,:].values/100
            result = minimize(f, params, constraints=cons, tol = 0.0001, bounds = bnds)
            new_params = result['x']
            self.volatility_matrix[i,:] = np.array([sabrVolatility(strike, fwd, expiryTime, *new_params)*100 for strike in self.moneyness])

        self.zerosurface = BlackVarianceSurface(
                                                    self.fx.today,               
                                                    self.fx.calendar,            
                                                    self.pillars,       
                                                    self.moneyness,             
                                                    self.volatility_matrix.T.tolist(),                
                                                    self.fx.day_count             
                                                )
        
        self.surface = BlackVolTermStructureHandle(self.zerosurface)

 












