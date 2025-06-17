from FxDerivative import Vanilla
import datetime as dt


strike = 1.18
date = dt.date(2026, 5, 5)
option_type = 'call'
N = 100000

option = Vanilla()

option.contract(option_type, strike, date, N)

print('Ref:', option.ref, 'option price:', round(option.Premium_EUR(),2), 'EUR')