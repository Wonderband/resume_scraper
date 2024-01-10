def get_code_from_sum(salary):
    if not salary:
        return 0
    amount = int(salary)
    if amount < 2000:
        return 0
    if amount <= 10000:
        return amount // 1000
    if amount < 15000:
        return 10
    if amount <= 30000:
        return 10 + (amount - 10000) // 5000
    if amount < 40000:
        return 14
    if amount < 50000:
        return 15
    if amount < 100000:
        return 16
    return 17


def get_code_from_years(input_years):
    years = int(input_years)
    if years <= 1:
        return years
    if years == 2:
        return 164
    if years <= 5:
        return 165
    return 166
