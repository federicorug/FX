import pandas as pd
import numpy as np
from xbbg import blp, pipeline
import datetime as dt
import scipy.interpolate as interpolate
from QuantLib import *
from scipy.optimize import minimize
from scipy.stats import norm
from RateHandle import rate as r
    


class Fx_data:
    def __init__(self):

        self.ticker_fx = 'EURUSD BGN Curncy'
        self.fields = ['Security_Name','mid']
        self.maturity = ['1W', '2W', '3W','1M', '2M', '3M', '6M', '9M', '12M', '2Y', '3Y', '4Y', '5Y', '7Y', '10Y']
        cal1 = TARGET()
        cal2 = UnitedStates(UnitedStates.NYSE)
        self.fx_calendar =  JointCalendar(cal1, cal2)
        self.today = dt.date.today()
        self.ql_today = Date(self.today.day, self.today.month, self.today.year)
        self.day_count = Actual360()
    
    def spot_data(self):

        self.spot = blp.bdp(self.ticker_fx, flds = self.fields)['mid'].values[0]


    def fwd_data(self):

        self.spot_data()
        self.tickerfwd = ['EUR{} Curncy'.format(i) for i in self.maturity]
        self.pts = [blp.bdp(i, flds= self.fields + ['maturity']) for i in self.tickerfwd]
        self.pts = pd.concat(self.pts, axis=0)
        self.fwd = self.spot + self.pts['mid'].values/10000
        self.expiry_dates = [self.fx_calendar.advance(Date(i.day, i.month, i.year), -2, Days) for i in self.pts['maturity']]
        interpolator  = Linear()           
        self.fx_fwd_curve = ForwardCurve(
            self.expiry_dates,
            self.fwd,
            self.day_count,
            self.fx_calendar,     )


    def fwd_interpolator(self, day):  

        self.fwd_data()
        target_date = Date(day.day, day.month, day.year)

        return self.fx_fwd_curve.zeroRate(target_date, self.day_count, Continuous, Annual).rate()

    def vol_data(self):

        self.fwd_data()
        self.maturity_v = self.maturity.copy()
        self.maturity_v[8] = '1Y'
        self.maturity_v = ['ON'] + self.maturity_v 

        atmvol = []
        rrvol25 = []
        rrvol10 = []    
        bfvol25 = []
        bfvol10 = []

        for i in self.maturity_v:
            
            ticker_atmvol = 'EURUSDV{} Curncy'.format(i) 
            ticker_rrvol25 = 'EURUSD25R{} Curncy'.format(i)
            ticker_rrvol10 = 'EURUSD10R{} Curncy'.format(i)   
            ticker_bfvol25 = 'EURUSD25B{} Curncy'.format(i)
            ticker_bfvol10 = 'EURUSD10B{} Curncy'.format(i)

            atmvol += [blp.bdp(ticker_atmvol, flds=['Security_Name', 'mid','maturity'])]
            rrvol25 += [blp.bdp(ticker_rrvol25, flds=['Security_Name', 'mid','maturity'])]
            rrvol10 += [blp.bdp(ticker_rrvol10, flds=['Security_Name', 'mid','maturity'])]
            bfvol25 += [blp.bdp(ticker_bfvol25, flds=['Security_Name', 'mid','maturity'])]
            bfvol10 += [blp.bdp(ticker_bfvol10, flds=['Security_Name', 'mid','maturity'])]

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
                     ]).T,  self.maturity_v, columns=['ATM','RR10','RR25','BF10','BF25'])
        
        self.surf['Call25'] = self.surf['ATM'] + self.surf['BF25'] + .5 * self.surf['RR25']
        self.surf['Call10'] = self.surf['ATM'] + self.surf['BF10'] + .5 * self.surf['RR10']
        self.surf['Put25'] = self.surf['ATM'] + self.surf['BF25'] - .5 * self.surf['RR25']
        self.surf['Put10'] = self.surf['ATM'] + self.surf['BF10'] - .5 * self.surf['RR10']
        self.surf['fwd'] = [self.spot] + list(self.fwd)

    def volbuilding(self):

        self.vol_data()
        self.estr = r()
        self.sofr = r()
        self.estr.data_take('EUR')
        self.sofr.data_take('USD')


        def strike_from_delta_forward(F, T, sigma , delta,  option_type='call'):

            sigma = sigma * 0.01   

            if option_type == 'call':

                d1 = np.array([norm.ppf(delta * np.exp(self.sofr.rate_interpolator(i) * self.day_count.yearFraction(self.ql_today,i))) if self.day_count.yearFraction(self.ql_today,i) < 1 else norm.ppf(delta) for i in T])

            else:
                delta = delta + 1

                d1 = np.array([norm.ppf(delta * np.exp(self.sofr.rate_interpolator(i) * self.day_count.yearFraction(self.ql_today,i))) if self.day_count.yearFraction(self.ql_today,i) < 1 else norm.ppf(delta) for i in T])
            
            tau = np.array([self.day_count.yearFraction(self.ql_today,i) for i in T])
            K = F * np.exp(-d1 * sigma * np.sqrt(tau) + 0.5 * sigma**2 * tau)
            return K
        
        self.expiry_dates = [self.fx_calendar.advance(self.ql_today, 1, Days)]  + self.expiry_dates
        self.K_call25 = strike_from_delta_forward(self.surf['fwd'].values, self.expiry_dates, self.surf['Call25'].values, 0.25,  option_type='call')
        self.K_call10 = strike_from_delta_forward(self.surf['fwd'].values, self.expiry_dates, self.surf['Call10'].values, 0.10,  option_type='call')
        self.K_Put25 = strike_from_delta_forward(self.surf['fwd'].values, self.expiry_dates, self.surf['Put25'].values,-0.25,  option_type='put')
        self.K_Put10 = strike_from_delta_forward(self.surf['fwd'].values, self.expiry_dates, self.surf['Put10'].values, -0.10, option_type='put')

        self.strike_surf = pd.DataFrame(np.array([ self.K_Put10, self.K_Put25, self.surf['fwd'].values, self.K_call25, self.K_call10]).T, self.maturity_v, columns=['put10','put25','atm','call25','call10'])

        self.moneyness = np.linspace(0.75, 1.25, 50) * self.spot
        self.volmat = np.zeros([len(self.K_Put10), len(self.moneyness)])
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
            strikes = self.strike_surf.iloc[i,:].values
            fwd = self.surf['fwd'].values[i]
            expiryTime = self.day_count.yearFraction(self.ql_today,self.expiry_dates[i])
            marketVols = self.surf[['Put10','Put25','ATM','Call25','Call10']].iloc[i,:].values/100
            result = minimize(f, params, constraints=cons, tol = 0.0001, bounds = bnds)
            new_params = result['x']
            self.volmat[i,:] = np.array([sabrVolatility(strike, fwd, expiryTime, *new_params)*100 for strike in self.moneyness])

        self.ql_surface = BlackVarianceSurface(
                                                    self.ql_today,               
                                                    self.fx_calendar,            
                                                    self.expiry_dates,       
                                                    self.moneyness,             
                                                    self.volmat.T.tolist(),                
                                                    self.day_count             
                                                )
        
        self.vol_handle = BlackVolTermStructureHandle(self.ql_surface)

 