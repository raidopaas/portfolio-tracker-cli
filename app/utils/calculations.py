

def calculate_allocation(balance, total):
    if balance is None or total == 0:
        return None

    return balance / total * 100