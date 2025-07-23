# FX Derivatives Pricing Framework

*A lightweight, Python-based playground for pricing foreign-exchange (FX) derivatives with live Bloomberg® data.*

---

## ✨ Why this project?

Foreign-exchange desks often prototype new pricing ideas before they make it into heavyweight risk engines.  
This repository is a **minimal, hack-friendly framework** that:

1. **Pulls market data** from the Bloomberg Desktop/Server API ;
2. **Builds elementary market objects** (spot, discount curves, vol surfaces);  
3. **Prices plain-vanilla European options** on **EUR / USD** with Black-Scholes.


---

## Current Feature Set

| Category                 | Status | Notes                                                    |
|--------------------------|:------:|----------------------------------------------------------|
| Bloomberg connectivity   | ✅     | Uses official  → live spot, vols, discount curve |
| Product coverage         | ⚠️     | European call/put, Digital options, Barrier options (knock-in / knock-out)                                    |
| Underlyings              | ⚠️     | `EURUSD` only                                            |
| Pricing model            | ✅     | Garman-Kohlhagen with SABR vols                       |


## 🛣️ Roadmap

The framework is in active development. Below are the key next steps:

- [ ] **QuantLib integration**  
  Replace internal pricing logic with QuantLib's robust analytical and numerical engines  
  _(local vol, SABR, Heston, Monte Carlo, Greeks, etc.)_

- [ ] **Additional derivatives**  
  Add support for:
  - One-touch and no-touch options
  - Asian options (arithmetic/geo average)
  - NDFs

- [ ] **More underlyings**  
  Expand coverage to:
  - `GBPUSD`, `USDJPY`, `EURGBP`
  - G10 crosses
  - Precious metals
  - Crypto-FX pairs (BTCUSD, ETHUSD)

- [ ] **Risk and analytics tools**  
  Implement tools for:
  - Delta / Gamma / Vega / Theta surfaces
  - Scenario analysis (shock ladders)
  - VaR / Expected Shortfall


---

## Quickstart

```bash
from FxDerivative import Vanilla, DigOption, BarOption
from QuantLib import *

vanilla = Vanilla()
vanilla.download_data()

digital = DigOption()
barrier = BarOption()
digital.mkt = vanilla.mkt
barrier.mkt = vanilla.mkt

strike = 1.19
date = Date(12, 1, 2026)
option_type = 'call'
N = 100000

vanilla.contract(option_type, strike, date, N)

ki = 1.21
barrier_type = 'knock-in'

barrier.contract(option_type, strike, barrier_type, ki,date, N)

digital.contract(option_type, strike, date, N)

print('Ref:', vanilla.ref, 'option price:', round(vanilla.Premium_EUR(),2), 'EUR')
print('Ref:', barrier.ref, 'option price:', round(barrier.Premium_EUR(),2), 'EUR')
print('Ref:', digital.ref, 'option price:', round(digital.Premium_EUR(),2), 'EUR')

Ref: 1.1739 option price: 1665.54 EUR
Ref: 1.1739 option price: 1657.2 EUR
Ref: 1.1739 option price: 39213.32 EUR
