import utils.console as console
import services.account_service as account_service

def validate_input(prompt, mapping):
    value = mapping.get(input(prompt))
    if not value:
        return None
    return value

def select_account(conn, transaction):
    accounts = account_service.get_accounts(conn)
    
    if not accounts:
        raise ValueError("No accounts available.")
    
    print_account_list(accounts)
    
    try:
        id_input = int(input(f"Enter account number for {transaction}: "))
    except Exception:
        raise ValueError("Invalid input. Transaction cancelled.")

    if id_input < 1 or id_input > len(accounts):
        raise ValueError("Invalid account number. Transaction cancelled.")
        
    return accounts[id_input - 1]

def print_account_list(accounts):
    index = 1

    print(f"{'Number':<5} {'Name':<20} {'Currency':<10}")

    for acc in accounts:
        print(f"{index:<5} {acc.name:<20} {acc.currency:<10}")
        index += 1