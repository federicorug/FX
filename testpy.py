from FxDerivative import Vanilla, BarOption
import datetime as dt

option = BarOption()

strike = 1.2
barrier = 1.23
barrier_type = 'knock-in'
date = dt.date(2026, 7, 3)
option_type = 'call'
N = 100000


option.contract(option_type, strike, barrier_type, barrier, date, N)

print('Ref:', option.ref, 'option price:', round(option.Premium_EUR(),2), 'EUR')