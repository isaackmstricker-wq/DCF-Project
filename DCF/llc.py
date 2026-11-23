from dcf import Company

def main():
    info = Company("assumptions_dcf.json")
    entry = info.get_info()

    print(entry["company"])

main()