from FxDerivative import Vanilla
from QuantLib import *



vanilla = Vanilla()
vanilla.download_data()




strike = 1.2

date = Date(7, 7, 2026)
option_type = 'call'
N = 100000

vanilla.contract(option_type, strike, date, N)

print('Ref:', vanilla.ref, 'option price:', round(vanilla.Premium_EUR(),2), 'EUR')
