from FxDerivative import Vanilla
from QuantLib import *



vanilla = Vanilla()
vanilla.download_data()


strike = 1.15

date = Date(12, 1, 2026)
option_type = 'put'
N = 100000

vanilla.contract(option_type, strike, date, N)

print('Ref:', vanilla.ref, 'option price:', round(vanilla.Premium_EUR(),2), 'EUR')
