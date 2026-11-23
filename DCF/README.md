# Discounted Cash Flow (DCF) Modeling with JSON Inputs
#### Description: A tool to compute Enterprise Value, Equity Value, and Implied Share Price given certain company information.

## Contents
1. Classes - Company, Discount
2. Enterprise Value
3. Equity Value
4. Implied Share Price

## Classes
### Company
The Company class instantiates a ```self.info``` instance variable and utilizes ```json.load()``` to convert a JSON file with the company's relevant information into dictionaries usable for the rest of the model. It then provides an external connection via ```Company().get_info()``` to access the dictionary. The class is broadly applicable to unpack JSON files into Python dictionaries.

**For the purposes of the DCF model, each company info JSON should be structured like the example:** [ExampleCorp JSON](path/to/assumptions_dcf.json)

    entry = Company(input("Company Info JSON: "))
    company = entry.get_info()

### Discount
The Discount class instantiates ```self.values```, ```self.rate```, and ```self.n``` instance variables to pull a list of future values to discount at the given rate and period. While the DCF will utilize the WACC (see below), this class is broadly applicable to return any present value calculation for a list or single value. For a list, the ```n``` argument should be omitted, and its default value ```None``` is used. Then, after discounting each value in values, it sums the results and returns them. If a single value is input, the ```n``` argument is required. Its external connection is ```Discount().get_pv()```

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

## Enterprise Value
Enterprise Value, or EV, is a measure of a company's total value to both debt and equity providers. It combines a company's market capitalization with its debt and subtracts its cash/cash equivalents. This makes EV a more comprehensive estimate of value than strictly market cap. In the world of mergers and acquisitions, this value tells capital providers the amount needed to purchase a company. Additionally, this model computes EV (and decedent values) by discounting unlevered free cash flow (UFCF) and terminal value (TV), focusing on company earnings to find intrinsic value.

    ent_v = Discount(true_ufcf, wacc(company)).get_pv() + 
    Discount(true_tv, wacc(company), company["projection_years"]).get_pv()

### WACC
In the model, the weighted average cost of capital (WACC) is computed as the discount rate for UFCFs and TV. Alternatively, it can be thought of as the required return for both debt and equity providers. Its function feeds into TV and EV calculations directly. The Company dictionary begins as an argument for the wacc function, which returns the WACC calculation:

    return (equity * capm) + (debt * debt_cost * (1 - tax))

**Importantly,** the wacc function accesses the value of the ```'equity_weight'``` and ```'debt_weight'``` keys in the Company dictionary, assuming them as JSON inputs previously calculated.

### UFCF
The unlevered free cash flows are those available to both debt and equity holders, so it flows into the EV calculation. The ufcf function returns the list of ufcfs for the duration of the period, which is passed into both the EV variable and tv function.

    true_ufcf = ufcf(company)
    true_tv = tv(company, ufcf(company), wacc(company))
    ent_v = Discount(true_ufcf, wacc(company)).get_pv() + 
    Discount(true_tv, wacc(company)).get_pv()

Each value/set in the UFCF calculation is made within the ufcf function, continually passed into lists that flow into the final UFCF calculation. For example, the period's NOPATS:

    nopats = []
    for ebit in ebits:
        nopats.append(ebit * (1 - tax))

And their use in the final calculation:

    _ufcfs = []
    for revenue, da, nopat, nwc in zip(revenues, das, nopats, nwcs):
        _ufcfs.append(
            nopat + da - (d["operating"]["capex_pct_revenue"] * revenue) - nwc
            )


### TV
The terminal value projects the value of cash flows following the period, making it an incredibly important assumption. **The model assumes perpetual/Gordon growth, meaning a constant growth rate is used.** While this method doesn't take the current market mood into account, it also doesn't assume the market will continue to treat the company the same in the future. 

    def tv(d: dict, u: list, w: float):
        return (u[-1] * (1 + d["terminal"]["growth_rate"])) / 
        (w - d["terminal"]["growth_rate"])

The function takes the company info dictionary, the ```_ufcfs``` list, and the wacc return value as arguments. It returns the TV itself as a single value for the last year of the projection. To sanity check the model, an Implied Exit Multiple is also printed in the results to compare against trading comparables/former M&As, calculated as EV/EBITDAn.

    def exit_ebitda(d: dict):
    revenue = d["operating"]["base_revenue"]
    growths = d["operating"]["revenue_growth"]
    margins = d["operating"]["ebitda_margin"]
    revenues, _ebitdas = [], []
    for growth, margin in zip(growths, margins):
        revenue *= (1 + growth)
        _ebitdas.append(revenue * margin)
    return _ebitdas[-1]
    ...
    multiple = true_tv / exit_ebitda(company)

## Equity Value
Equity Value, or EqV, is a measure of a company's residual value for common stockholders after lenders', preferred shareholders', and minority shares' equity is removed. The model calculates EqV by using EV:

    equ_v = (ent_v - (company["balance_sheet"]["debt"]) +
        (company["balance_sheet"]["cash"]) - (company["balance_sheet"]["preferred"]) -
        (company["balance_sheet"]["non_interest"]))

## Implied Share Price
From EqV, dividing by the company's number of outstanding shares provides an implied share price based on the company's intrinsic value. Therefore, it provides a key indicator in the market price's variance from the true value of the company. The number of outstanding shares is another dictionary input.

    share_price = equ_v / (company["balance_sheet"]["outstanding"])

#### Finally, the EV, EqV, and Implied Share Price are all printed, showing their values for the company. The EV and EqV are displayed in the specified units, while Share Price is assumed in USD.
    Company Info JSON: assumptions_dcf.json
    DCF Results for ExampleCorp
    Enterprise Value: 1,459.9810 USD millions
    Equity Value: 1,309.9810 USD millions
    Share Price: $13.10
    Implied Exit Multiple: 10
