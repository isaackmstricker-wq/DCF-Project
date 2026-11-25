import json

def main():
    print("Notes: Input percentages/rates as decimals, and if units are defined, input values in said units.")
    filename = input("File name: ")
    if filename.endswith(".json"):
        filename = filename.rstrip(".json")
    new_file(filename, file_info())

def file_info():
    rev_growths = [float(g) for g in input("Revenue growth per year of period: ").split(",")]
    ebitda_margins = [float(e) for e in input("EBITDA margin per year of period: ").split(",")]

    data = {
        "company": input("Company Name: "),
        "units": input("Units (i.e. USD millions): "),
        "projection_years": int(input("Projection Years: ")),

        "operating": {
            "base_revenue": float(input("Year 0/Baseline Revenue: ")),
            "revenue_growth": rev_growths,
            "ebitda_margin": ebitda_margins,
            "da_pct_rev": float(input("Depreciation & Amortization as % Revenue: ")),
            "capex_pct_rev": float(input("Capital Expenditure as % Revenue: ")),
            "nwc_pct_rev": float(input("Net Working Capital as % Revenue: ")),
            "tax_rate": float(input("Total Tax Rate: "))
        },

        "wacc": {
            "risk_free_rate": float(input("Risk-free Rate: ")),
            "beta": float(input("Beta: ")),
            "equity_risk_premium": float(input("Equity Risk Premium: ")),
            "pre_tax_cost": float(input("Pre-tax Cost of Debt: ")),
            "debt_weight": float(input("Weight of Debt: "))
        },

        "terminal": {
            "growth_rate": float(input("Assumed growth rate: "))
        },

        "balance_sheet": {
        "debt": float(input("Debt Value: ")),
        "equity": float(input("Common Equity Value: ")),
        "preferred": float(input("Preferred Shares Value: ")),
        "non_interest": float(input("Value of Non-controlling Interest: ")),
        "cash": float(input("Cash On Hand: ")),
        "outstanding": float(input("Number of Shares Outstanding: "))
        }
    }
    return data

def new_file(filename, company):
    with open(f"{filename}.json", "w", encoding="utf-8") as file:
        json.dump(company, file, indent=4)


if __name__ == "__main__":
    main()