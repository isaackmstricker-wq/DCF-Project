from dcf import Company
from dcf import Discount

# import Company information

# max EV = max entry equity / (1 + IRR target)^n
def main():
    info = Company(input("Company Info JSON:"))
    entry = info.get_info()

    # returned fcf and ebitda of last year
    end_fcf, end_ebitda = _fcf(entry)
    exit_ev = entry["lbo"]["exit_multiple"] * end_ebitda
    exit_equity = exit_ev - (end_fcf - entry["balance_sheet"]["cash"])
    moic = exit_equity / ((entry["lbo"]["entry_multiple"] - entry["lbo"]["debt_to_ebitda"]) * entry["lbo"]["entry_ebitda"])
    irr = moic**(1 / entry["lbo"]["holding_years"]) - 1

    max_entry_eq = Discount(exit_equity, entry["lbo"]["target_irr"], entry["lbo"]["holding_years"]).get_pv()
    max_ent_v = max_entry_eq + (entry["lbo"]["debt_to_ebitda"] * entry["lbo"]["entry_ebitda"])

    print(f"Max Enterprise Value: {max_ent_v:,.2f}")
    print(f"Max Entry Equity: {max_entry_eq:,.2f}")


def _fcf(d: dict):
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
    all_revs = [d["operating"]["base_revenue"]] + revenues
    nwcs = [
        d["operating"]["nwc_pct_rev"] * (all_revs[i] - all_revs[i - 1])
        for i in range(1, len(all_revs))
        ]
    # return free cash flows
    balance = d["lbo"]["entry_ebitda"] * d["lbo"]["debt_to_ebitda"]
    schedule = []
    for revenue, ebit, da, nwc in zip(revenues, ebits, das, nwcs):
        interest = balance * d["lbo"]["interest_rate"]
        # FCF = EBIT - interest + DA - Tax on EBT - change in NWC - capex
        fcf = ebit - interest + da - ((ebit - interest) * tax) - nwc - (d["operating"]["capex_pct_rev"] * revenue)
        closing = balance - (fcf * d["lbo"]["cash_sweep_pct"])
        schedule.append(closing)
        balance = closing
    return schedule[-1], _ebitdas[-1]

def sensitivity():
    


# test sources = uses

if __name__ == "__main__":
    main()