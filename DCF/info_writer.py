import json

def main():
    filename = input("File name: ")
    if filename.endswith(".json"):
        filename = filename.rstrip(".json")
    new_file(filename, file_info())

def file_info():
    data = {
        "company": input("Company Name: "),
        "units": input("Units (i.e. USD millions): "),
        "projection_years": int(input("Projection Years: ")),

        "operating": {
            "base_revenue": 500.0,
            "revenue_growth": [0.10, 0.09, 0.08, 0.07, 0.06],
            "ebitda_margin": [0.22, 0.22, 0.23, 0.23, 0.24],
            "da_pct_rev": 0.04,
            "capex_pct_rev": 0.05,
            "nwc_pct_rev": 0.10,
            "tax_rate": 0.25
        },

        "wacc": {
            "risk_free_rate": 0.04,
            "beta": 1.1,
            "equity_risk_premium": 0.055,
            "pre_tax_cost": 0.06,
            "debt_weight": 0.30
        },

        "terminal": {
            "growth_rate": 0.025
        },

        "balance_sheet": {
        "debt": 200.0,
        "preferred": 0.0,
        "non_interest": 0.0,
        "cash": 50.0,
        "outstanding": 100.0
        }
    }
    return data

def new_file(filename, company):
    with open(f"{filename}.json", "w", encoding="utf-8") as file:
        json.dump(company, file, indent=4)


if __name__ == "__main__":
    main()