from FxDerivative import VanillaOption
import datetime as dt


strike = 1.16
date = dt.date(2026, 1, 2)
option_type = 'call'
N = 100000

option = VanillaOption()

option.contract(option_type, strike, date, N)

print('Ref:', option.ref, 'option price:', round(option.Premium_EUR(),2), 'EUR')