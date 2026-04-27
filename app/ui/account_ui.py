import utils.console as console
import services.account_service as account_service
from ui.helpers import validate_input

def add_account_ui(conn):
    type_map = {
        "1": "cash",
        "2": "broker"
    }
    currency_map = {
        "1": "EUR",
        "2": "USD"
    }

    console.clear_screen()

    name = input("Enter new account's name: ").strip()

    print("Select new account's type.")
    type_input = "Enter '1' for cash account or enter '2' for broker account: "
    account_type = validate_input(type_input, type_map)
    if not account_type:
        console.clear_screen()
        print("Invalid input. Adding new account cancelled.")
        return
    
    print("Select new account's currency.")
    currency_input = "Enter '1' for EUR or enter '2' for USD: "
    currency = validate_input(currency_input, currency_map)
    if not currency:
        console.clear_screen()
        print("Invalid input. Adding new account cancelled.")
        return
    
    try:
        account_service.add_account(conn, name, account_type, currency)
        console.clear_screen()
        print("New account added successfully.")
    except Exception as e:
        console.clear_screen()
        print(e)