# FX Derivatives Pricing Framework

*A lightweight, Python-based playground for pricing foreign-exchange (FX) derivatives with live Bloomberg® data.*

---

## ✨ Why this project?

Foreign-exchange desks often prototype new pricing ideas before they make it into heavyweight risk engines.  
This repository is a **minimal, hack-friendly framework** that:

1. **Pulls market data** from the Bloomberg Desktop/Server API ;
2. **Builds elementary market objects** (spot, discount curves, vol surfaces);  
3. **Prices plain-vanilla European options** on **EUR / USD** with Black-Scholes.

It is intentionally small: one deal type, one underlying, one model—so you can read the entire codebase over a coffee.

---

## Current Feature Set

| Category                 | Status | Notes                                                    |
|--------------------------|:------:|----------------------------------------------------------|
| Bloomberg connectivity   | ✅     | Uses official  → live spot, vols, discount curve |
| Product coverage         | ⚠️     | European call/put only                                   |
| Underlyings              | ⚠️     | `EURUSD` only                                            |
| Pricing model            | ✅     | Garman-Kohlhagen with SABR vols                       |


## 🛣️ Roadmap

The framework is in active development. Below are the key next steps:

- [ ] **QuantLib integration**  
  Replace internal pricing logic with QuantLib's robust analytical and numerical engines  
  _(local vol, SABR, Heston, Monte Carlo, Greeks, etc.)_

- [ ] **Additional derivatives**  
  Add support for:
  - Digital options
  - One-touch and no-touch options
  - Barrier options (knock-in / knock-out)
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
from FxDerivative import VanillaOption
import datetime as dt

strike = 1.16
date = dt.date(2026, 1, 2)
option_type = 'call'
N = 100000

option = VanillaOption()
option.contract(option_type, strike, date, N)
premium = round(option.Premium_EUR(),2)

print('Ref:', option.ref, 'option price:',premium , 'EUR', 'implied vol:', option.sigma)

Ref: 1.15555 option price: 2378.0 EUR implied vol: 0.07770351720145457
