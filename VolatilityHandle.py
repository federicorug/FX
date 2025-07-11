
# import pandas as pd
# import numpy as np
# from xbbg import blp, pipeline
# import datetime as dt
# import scipy.interpolate as interpolate
# from QuantLib import *
# from scipy.optimize import minimize
# from scipy.stats import norm
# from RateHandle import RateCurve 
# from FXHandle import FXCurve
# import matplotlib.pyplot as plt


# class VolSurface:
#     def __init__(self): 
        
#         self.maturity = ['ON','1W', '2W', '3W','1M', '2M', '3M', '6M', '9M', '1Y', '2Y', '3Y', '4Y', '5Y', '7Y', '10Y']

#         atmvol = []
#         rrvol35 = []
#         rrvol25 = []
#         rrvol15 = []
#         rrvol10 = [] 
#         rrvol5 = [] 
#         bfvol35 = []
#         bfvol25 = []
#         bfvol15 = []
#         bfvol10 = []
#         bfvol5 = [] 
        
#         for i in self.maturity:
#             atmvol += [blp.bdp('EURUSDV{} Curncy'.format(i) , flds=['Security_Name', 'mid','maturity'])]
#             rrvol35 += [blp.bdp('EURUSD35R{} Curncy'.format(i), flds=['Security_Name', 'mid','maturity'])]
#             rrvol25 += [blp.bdp('EURUSD25R{} Curncy'.format(i), flds=['Security_Name', 'mid','maturity'])]
#             rrvol15+= [blp.bdp('EURUSD15R{} Curncy'.format(i), flds=['Security_Name', 'mid','maturity'])]
#             rrvol10 += [blp.bdp('EURUSD10R{} Curncy'.format(i)  , flds=['Security_Name', 'mid','maturity'])]
#             rrvol5 += [blp.bdp('EURUSD5R{} Curncy'.format(i)  , flds=['Security_Name', 'mid','maturity'])]
#             bfvol35 += [blp.bdp('EURUSD35B{} Curncy'.format(i), flds=['Security_Name', 'mid','maturity'])]
#             bfvol25 += [blp.bdp('EURUSD25B{} Curncy'.format(i), flds=['Security_Name', 'mid','maturity'])]
#             bfvol15 += [blp.bdp('EURUSD15B{} Curncy'.format(i), flds=['Security_Name', 'mid','maturity'])]
#             bfvol5 += [blp.bdp('EURUSD5B{} Curncy'.format(i), flds=['Security_Name', 'mid','maturity'])]
#             bfvol10 += [blp.bdp('EURUSD10B{} Curncy'.format(i), flds=['Security_Name', 'mid','maturity'])]  

#         atmvol = pd.concat(atmvol, axis=0)
#         rrvol35 = pd.concat(rrvol35, axis=0)
#         rrvol25 = pd.concat(rrvol25, axis=0)
#         rrvol15 = pd.concat(rrvol15, axis=0)
#         rrvol10 = pd.concat(rrvol10, axis=0)
#         rrvol5 = pd.concat(rrvol5, axis=0)
#         bfvol35 = pd.concat(bfvol35, axis=0)
#         bfvol25 = pd.concat(bfvol25, axis=0)
#         bfvol15 = pd.concat(bfvol15, axis=0)
#         bfvol10 = pd.concat(bfvol10, axis=0)
#         bfvol5 = pd.concat(bfvol5, axis=0)

#         self.surf = pd.DataFrame(np.array([atmvol['mid'].values,
#                                            rrvol5['mid'].values,
#                         rrvol10['mid'].values,
#                         rrvol15['mid'].values,
#                         rrvol25['mid'].values,
#                         rrvol35['mid'].values,
#                         bfvol5['mid'].values,
#                         bfvol10['mid'].values,
#                         bfvol15['mid'].values,
#                         bfvol25['mid'].values,
#                         bfvol35['mid'].values,

#                         ]).T,  self.maturity, columns=['ATM','RR5','RR10','RR15','RR25','RR35','BF5','BF10','BF15','BF25','BF35'])

#         self.surf['Call35'] = self.surf['ATM'] + self.surf['BF35'] + .5 * self.surf['RR35']
#         self.surf['Call25'] = self.surf['ATM'] + self.surf['BF25'] + .5 * self.surf['RR25']
#         self.surf['Call15'] = self.surf['ATM'] + self.surf['BF15'] + .5 * self.surf['RR15']
#         self.surf['Call10'] = self.surf['ATM'] + self.surf['BF10'] + .5 * self.surf['RR10']
#         self.surf['Call5'] = self.surf['ATM'] + self.surf['BF5'] + .5 * self.surf['RR5']
#         self.surf['Put35'] = self.surf['ATM'] + self.surf['BF35'] - .5 * self.surf['RR35']
#         self.surf['Put25'] = self.surf['ATM'] + self.surf['BF25'] - .5 * self.surf['RR25']
#         self.surf['Put15'] = self.surf['ATM'] + self.surf['BF15'] - .5 * self.surf['RR15']
#         self.surf['Put10'] = self.surf['ATM'] + self.surf['BF10'] - .5 * self.surf['RR10']
#         self.surf['Put5'] = self.surf['ATM'] + self.surf['BF5'] - .5 * self.surf['RR5']


#     def building(self):

#         self.estr = RateCurve()
#         self.sofr = RateCurve()
#         self.estr.data_take('EUR')
#         self.sofr.data_take('USD')
#         self.fx = FXCurve()
#         self.fx.data_take()

#         def strike_from_delta_forward(F, T, sigma , delta,  option_type='call'):

#             sigma = sigma * 0.01   

#             if option_type == 'call':
                
#                 d1 = np.array([norm.ppf(delta * np.exp(self.estr.rate_interpolator(i) * self.fx.day_count.yearFraction(self.fx.today,i))) if self.fx.day_count.yearFraction(self.fx.today,i) < 1 else norm.ppf(delta) for i in T])
               
#             else:
#                 delta = delta + 1
#                 d1 = np.array([norm.ppf(delta * np.exp(self.estr.rate_interpolator(i) * self.fx.day_count.yearFraction(self.fx.today,i))) if self.fx.day_count.yearFraction(self.fx.today,i) < 1 else norm.ppf(delta) for i in T])
            
#             tau = np.array([self.fx.day_count.yearFraction(self.fx.today,i) for i in T])
#             K = self.fx.spot / np.exp(d1 * sigma * np.sqrt(tau) - (self.sofr.rate_interpolator(T)- self.estr.rate_interpolator(T) + 0.5 * sigma**2 )* tau) 

#             return K
        
#         self.atm_strikes = np.insert(self.fx.forward_rates, 0 , self.fx.spot)
#         self.pillars = [self.fx.calendar.advance(self.fx.today, 1, Days)]  + self.fx.pillars
#         self.K_call35 = strike_from_delta_forward(self.fx.forward_rates, self.pillars, self.surf['Call35'].values, 0.35,  option_type='call')
#         self.K_call25 = strike_from_delta_forward(self.fx.forward_rates, self.pillars, self.surf['Call25'].values, 0.25,  option_type='call')
#         self.K_call15 = strike_from_delta_forward(self.fx.forward_rates, self.pillars, self.surf['Call15'].values, 0.15,  option_type='call')
#         self.K_call10 = strike_from_delta_forward(self.fx.forward_rates, self.pillars, self.surf['Call10'].values, 0.10,  option_type='call')
#         self.K_call5 = strike_from_delta_forward(self.fx.forward_rates, self.pillars, self.surf['Call5'].values, 0.05,  option_type='call')
#         self.K_Put5 = strike_from_delta_forward(self.fx.forward_rates, self.pillars, self.surf['Put5'].values, -0.05,  option_type='put')
#         self.K_Put35 = strike_from_delta_forward(self.fx.forward_rates, self.pillars, self.surf['Put35'].values,-0.35,  option_type='put')
#         self.K_Put25 = strike_from_delta_forward(self.fx.forward_rates, self.pillars, self.surf['Put25'].values,-0.25,  option_type='put')
#         self.K_Put15 = strike_from_delta_forward(self.fx.forward_rates, self.pillars, self.surf['Put15'].values,-0.15,  option_type='put')
#         self.K_Put10 = strike_from_delta_forward(self.fx.forward_rates, self.pillars, self.surf['Put10'].values, -0.10, option_type='put')

#         self.strike_surface = pd.DataFrame(np.array([ self.K_Put5 , self.K_Put10, self.K_Put15,self.K_Put25, self.K_Put35,self.atm_strikes ,self.K_call35, self.K_call25,self.K_call15, self.K_call10,self.K_call5]).T,
#                                            self.maturity, columns=['put5','put10','put15','put25','put35','atm','call35','call25','call15','call10','call5'])

#         self.moneyness = np.linspace(0.75, 1.25, 50) * self.fx.spot
#         self.volatility_matrix = np.zeros([len(self.K_Put10), len(self.moneyness)])
        
#         for i in range(len(self.K_Put10)):

#             strikes = list(self.strike_surface.iloc[i,:].values)
#             fwd = self.atm_strikes[i]
#             expiryTime = self.fx.day_count.yearFraction(self.fx.today,self.pillars[i])
#             marketVols = list(self.surf[['Put5','Put10','Put15','Put25','Put35','ATM','Call35','Call25','Call15','Call10','Call5']].iloc[i,:].values/100)
          
#             beta = 0.5
#             sabr = SABRInterpolation(
#                 strikes,
#                 marketVols,
#                 expiryTime,
#                 fwd,
#                 alpha=0.2,   
#                 beta=beta,
#                 nu=0.3,      
#                 rho=0.0,     
#                 alphaIsFixed=False,
#                 betaIsFixed=True,  
#                 nuIsFixed=False,
#                 rhoIsFixed=False
#             )

#             # print('T {}:'.format(expiryTime),"Alpha =", sabr.alpha(), "Beta  =", "Nu    =", sabr.nu(),"Rho   =", sabr.rho())
#             # plt.plot(strikes, [sabr(strike) for strike in strikes], label='sabr interpolation')
#             # plt.title('{}'.format(expiryTime))
#             # plt.plot(strikes, marketVols, label='market')
#             # plt.plot(strikes, [sabrVolatility(strike, fwd, expiryTime, sabr.alpha() ,sabr.beta(), sabr.nu(), sabr.rho()) for strike in strikes], label='sabr model')
#             # plt.legend()
#             # plt.show()

#             self.volatility_matrix[i,:] = np.array([sabrVolatility(strike, fwd, expiryTime, sabr.alpha() ,sabr.beta(), sabr.nu(), sabr.rho())for strike in self.moneyness])

#         self.zerosurface = BlackVarianceSurface(
#                                                     self.fx.today,               
#                                                     self.fx.calendar,            
#                                                     self.pillars,       
#                                                     self.moneyness,             
#                                                     self.volatility_matrix.T.tolist(),                
#                                                     Actual360()           
#                                                 )
#         self.volatility_matrix = pd.DataFrame(self.volatility_matrix, columns=self.moneyness, index=self.pillars)
#         self.volatility_matrix.index.name = 'maturity'
#         self.volatility_matrix.columns.name = 'moneyness'
#         self.surface = BlackVolTermStructureHandle(self.zerosurface)




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
        self.isin = ['EURUSDV','EURUSD5R','EURUSD10R','EURUSD15R','EURUSD25R','EURUSD35R','EURUSD5B','EURUSD10B','EURUSD15B','EURUSD25B','EURUSD35B']
        self.mkt_vola_struct = []
        self.surface_index = ['ATM','RR5','RR10','RR15','RR25','RR35','BF5','BF10','BF15','BF25','BF35']
        self.surf = pd.DataFrame()

        # atmvol = []
        # rrvol35 = []
        # rrvol25 = []
        # rrvol15 = []
        # rrvol10 = [] 
        # rrvol5 = [] 
        # bfvol35 = []
        # bfvol25 = []
        # bfvol15 = []
        # bfvol10 = []
        # bfvol5 = [] 
        
        # for i in self.maturity:
        #     atmvol += [blp.bdp('EURUSDV{} Curncy'.format(i) , flds=['Security_Name', 'mid','maturity'])]
        #     rrvol35 += [blp.bdp('EURUSD35R{} Curncy'.format(i), flds=['Security_Name', 'mid','maturity'])]
        #     rrvol25 += [blp.bdp('EURUSD25R{} Curncy'.format(i), flds=['Security_Name', 'mid','maturity'])]
        #     rrvol15+= [blp.bdp('EURUSD15R{} Curncy'.format(i), flds=['Security_Name', 'mid','maturity'])]
        #     rrvol10 += [blp.bdp('EURUSD10R{} Curncy'.format(i)  , flds=['Security_Name', 'mid','maturity'])]
        #     rrvol5 += [blp.bdp('EURUSD5R{} Curncy'.format(i)  , flds=['Security_Name', 'mid','maturity'])]
        #     bfvol35 += [blp.bdp('EURUSD35B{} Curncy'.format(i), flds=['Security_Name', 'mid','maturity'])]
        #     bfvol25 += [blp.bdp('EURUSD25B{} Curncy'.format(i), flds=['Security_Name', 'mid','maturity'])]
        #     bfvol15 += [blp.bdp('EURUSD15B{} Curncy'.format(i), flds=['Security_Name', 'mid','maturity'])]
        #     bfvol5 += [blp.bdp('EURUSD5B{} Curncy'.format(i), flds=['Security_Name', 'mid','maturity'])]
        #     bfvol10 += [blp.bdp('EURUSD10B{} Curncy'.format(i), flds=['Security_Name', 'mid','maturity'])]  

        # atmvol = pd.concat(atmvol, axis=0)
        # rrvol35 = pd.concat(rrvol35, axis=0)
        # rrvol25 = pd.concat(rrvol25, axis=0)
        # rrvol15 = pd.concat(rrvol15, axis=0)
        # rrvol10 = pd.concat(rrvol10, axis=0)
        # rrvol5 = pd.concat(rrvol5, axis=0)
        # bfvol35 = pd.concat(bfvol35, axis=0)
        # bfvol25 = pd.concat(bfvol25, axis=0)
        # bfvol15 = pd.concat(bfvol15, axis=0)
        # bfvol10 = pd.concat(bfvol10, axis=0)
        # bfvol5 = pd.concat(bfvol5, axis=0)

        for j, isi in enumerate(self.isin):
            self.surf['{}'.format(self.surface_index[j])] = pd.concat([blp.bdp('{}{} Curncy'.format(isi,i) , flds=['Security_Name', 'mid','maturity']) 
                       for i in ['ON','1W', '2W', '3W','1M', '2M', '3M', '6M', '9M', '1Y', '2Y', '3Y', '4Y', '5Y', '7Y', '10Y']], axis=0)


        self.surf = pd.DataFrame(np.array([atmvol['mid'].values,
                                           rrvol5['mid'].values,
                        rrvol10['mid'].values,
                        rrvol15['mid'].values,
                        rrvol25['mid'].values,
                        rrvol35['mid'].values,
                        bfvol5['mid'].values,
                        bfvol10['mid'].values,
                        bfvol15['mid'].values,
                        bfvol25['mid'].values,
                        bfvol35['mid'].values,

                        ]).T,  self.maturity, columns = self.surface_index)

        self.surf['Call35'] = self.surf['ATM'] + self.surf['BF35'] + .5 * self.surf['RR35']
        self.surf['Call25'] = self.surf['ATM'] + self.surf['BF25'] + .5 * self.surf['RR25']
        self.surf['Call15'] = self.surf['ATM'] + self.surf['BF15'] + .5 * self.surf['RR15']
        self.surf['Call10'] = self.surf['ATM'] + self.surf['BF10'] + .5 * self.surf['RR10']
        self.surf['Call5'] = self.surf['ATM'] + self.surf['BF5'] + .5 * self.surf['RR5']
        self.surf['Put35'] = self.surf['ATM'] + self.surf['BF35'] - .5 * self.surf['RR35']
        self.surf['Put25'] = self.surf['ATM'] + self.surf['BF25'] - .5 * self.surf['RR25']
        self.surf['Put15'] = self.surf['ATM'] + self.surf['BF15'] - .5 * self.surf['RR15']
        self.surf['Put10'] = self.surf['ATM'] + self.surf['BF10'] - .5 * self.surf['RR10']
        self.surf['Put5'] = self.surf['ATM'] + self.surf['BF5'] - .5 * self.surf['RR5']


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
        self.K_call35 = strike_from_delta_forward(self.fx.forward_rates, self.pillars, self.surf['Call35'].values, 0.35,  option_type='call')
        self.K_call25 = strike_from_delta_forward(self.fx.forward_rates, self.pillars, self.surf['Call25'].values, 0.25,  option_type='call')
        self.K_call15 = strike_from_delta_forward(self.fx.forward_rates, self.pillars, self.surf['Call15'].values, 0.15,  option_type='call')
        self.K_call10 = strike_from_delta_forward(self.fx.forward_rates, self.pillars, self.surf['Call10'].values, 0.10,  option_type='call')
        self.K_call5 = strike_from_delta_forward(self.fx.forward_rates, self.pillars, self.surf['Call5'].values, 0.05,  option_type='call')
        self.K_Put5 = strike_from_delta_forward(self.fx.forward_rates, self.pillars, self.surf['Put5'].values, -0.05,  option_type='put')
        self.K_Put35 = strike_from_delta_forward(self.fx.forward_rates, self.pillars, self.surf['Put35'].values,-0.35,  option_type='put')
        self.K_Put25 = strike_from_delta_forward(self.fx.forward_rates, self.pillars, self.surf['Put25'].values,-0.25,  option_type='put')
        self.K_Put15 = strike_from_delta_forward(self.fx.forward_rates, self.pillars, self.surf['Put15'].values,-0.15,  option_type='put')
        self.K_Put10 = strike_from_delta_forward(self.fx.forward_rates, self.pillars, self.surf['Put10'].values, -0.10, option_type='put')

        self.strike_surface = pd.DataFrame(np.array([ self.K_Put5 , self.K_Put10, self.K_Put15,self.K_Put25, self.K_Put35,self.atm_strikes ,self.K_call35, self.K_call25,self.K_call15, self.K_call10,self.K_call5]).T,
                                           self.maturity, columns=['put5','put10','put15','put25','put35','atm','call35','call25','call15','call10','call5'])

        self.moneyness = np.linspace(0.75, 1.25, 50) * self.fx.spot
        self.volatility_matrix = np.zeros([len(self.K_Put10), len(self.moneyness)])
        
        for i in range(len(self.K_Put10)):

            strikes = list(self.strike_surface.iloc[i,:].values)
            fwd = self.atm_strikes[i]
            expiryTime = self.fx.day_count.yearFraction(self.fx.today,self.pillars[i])
            marketVols = list(self.surf[['Put5','Put10','Put15','Put25','Put35','ATM','Call35','Call25','Call15','Call10','Call5']].iloc[i,:].values/100)
          
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
