from FxDerivative import Vanilla, BarOption
import datetime as dt

vanilla = Vanilla()
vanilla.download_data()
barriera = BarOption()
barriera.mkt = vanilla.mkt


strike = 1.2
barrier = 1.3
barrier_type = 'knock-in'
date = dt.date(2026, 7, 3)
option_type = 'call'
N = 100000

vanilla.contract(option_type, strike, date, N)
barriera.contract(option_type, strike, barrier_type, barrier, date, N)

print('Ref:', vanilla.ref, 'option price:', round(vanilla.Premium_EUR(),2), 'EUR')
print('Ref:', barriera.ref, 'option price:', round(barriera.Premium_EUR(),2), 'EUR')