import json
import sys

class Company:
    def __init__(self, info: str):
        self._info = info
        if self._info.endswith(".json"):
            self.load_assumptions()
        else:
            sys.exit("Incorrect type: load JSON file")

    # Load in company JSON as dict
    def load_assumptions(self):
        with open(self._info, "r") as file:
            return json.load(file)

    # External access
    def get_info(self):
        return self.load_assumptions()

# Apply discounting to any FV
class Discount:
    def __init__(self, values, rate, n=None):
        self.values = values
        self.rate = rate
        self.n = n

    def pvsum(self):
        if type(self.values) == list:
            self.pvs = [v / (1 + self.rate)**t for t, v in enumerate(self.values, start=1)]
            return sum(self.pvs)
        else:
            return self.values / (1 + self.rate)**self.n

    def get_pv(self):
        return self.pvsum()

def main():
    # Pull dictionary
    if len(sys.argv) == 2:
        entry = Company(sys.argv[1])
    else:
        entry = Company(input("Company Info JSON: "))
    company = entry.get_info()

    # Final equation
    true_ufcf = ufcf(company)
    true_tv = tv(company, ufcf(company), wacc(company))
    multiple = true_tv / exit_ebitda(company)
    ent_v = Discount(true_ufcf, wacc(company)).get_pv() + Discount(true_tv, wacc(company), company["projection_years"]).get_pv()
    equ_v = (ent_v - (company["balance_sheet"]["debt"]) +
        (company["balance_sheet"]["cash"]) - (company["balance_sheet"]["preferred"]) -
        (company["balance_sheet"]["non_interest"]))
    share_price = equ_v / (company["balance_sheet"]["outstanding"])

    print(f"DCF Results for {company["company"]}")
    print(f"Enterprise Value: {ent_v:,.4f} {company["units"]}")
    print(f"Equity Value: {equ_v:,.4f} {company["units"]}")
    print(f"Share Price: ${share_price:,.2f}")
    print(f"Implied Exit Multiple: {multiple:.0f}")

def exit_ebitda(d: dict):
    revenue = d["operating"]["base_revenue"]
    growths = d["operating"]["revenue_growth"]
    margins = d["operating"]["ebitda_margin"]
    revenues, _ebitdas = [], []
    for growth, margin in zip(growths, margins):
        revenue *= (1 + growth)
        _ebitdas.append(revenue * margin)
    return _ebitdas[-1]

def ufcf(d: dict):
    revenue = d["operating"]["base_revenue"]
    growths = d["operating"]["revenue_growth"]
    margins = d["operating"]["ebitda_margin"]
    tax = d["operating"]["tax_rate"]
    # Build revenue and ebitda lists
    revenues, _ebitdas = [], []
    for growth, margin in zip(growths, margins):
        revenue *= (1 + growth)
        revenues.append(revenue)
        _ebitdas.append(revenue * margin)
    # Each revenue times da_pct = da
    das = []
    for revenue in revenues:
        das.append(revenue * d["operating"]["da_pct_rev"])
    # Each ebitda minus each da
    ebits = []
    for ebitda, da in zip(_ebitdas, das):
        ebits.append(ebitda - da)

    nopats = []
    for ebit in ebits:
        nopats.append(ebit * (1 - tax))
    # Make list of revenues and take nwc change
    all_revs = [d["operating"]["base_revenue"]] + revenues
    nwcs = [
        d["operating"]["nwc_pct_rev"] * (all_revs[i] - all_revs[i - 1])
        for i in range(1, len(all_revs))
        ]

    _ufcfs = []
    for revenue, da, nopat, nwc in zip(revenues, das, nopats, nwcs):
        _ufcfs.append(
            nopat + da - (d["operating"]["capex_pct_rev"] * revenue) - nwc
            )
    return _ufcfs

def tv(d: dict, u: list, w):
    # Perpetuity growth method of Terminal Value
    # (UFCFn x (1 + g)) / (wacc - g)
    return (u[-1] * (1 + d["terminal"]["growth_rate"])) / (w - d["terminal"]["growth_rate"])

def wacc(d: dict):
    equity_weight = 1 - d["wacc"]["debt_weight"]
    debt_weight = d["wacc"]["debt_weight"]
    capm = d["wacc"]["risk_free_rate"] + (d["wacc"]["beta"] * d["wacc"]["equity_risk_premium"])
    debt_cost = d["wacc"]["pre_tax_cost"]
    tax = d["operating"]["tax_rate"]

    return (equity_weight * capm) + (debt_weight * debt_cost * (1 - tax))

if __name__ == "__main__":
    main()
