import utils.console as console

def validate_input(prompt, mapping):
    value = mapping.get(input(prompt))
    if not value:
        return None
    return value

def print_account_list(accounts):
    id = 1

    print(f"{'ID':<5} {'Name':<20} {'Currency':<10}")

    for acc in accounts:
        print(f"{id:<5} {acc.name:<20} {acc.currency:<10}")
        id += 1