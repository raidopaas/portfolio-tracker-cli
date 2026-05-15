import utils.console as console
import services.account_service as account_service
import services.stock_service as stock_service
import ui.helpers as helpers

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
    account_type = helpers.validate_input(type_input, type_map)
    if not account_type:
        console.clear_screen()
        print("Invalid input. Adding new account cancelled.")
        return
    
    print("Select new account's currency.")
    currency_input = "Enter '1' for EUR or enter '2' for USD: "
    currency = helpers.validate_input(currency_input, currency_map)
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

def remove_account_ui(conn):
    console.clear_screen()

    try:
        account = helpers.select_account(conn, "removal")
    except Exception as e:
        console.clear_screen()
        print(e)
        return
    
    approved = account_service.validate_account_removal(conn, account)

    if not approved:
        console.clear_screen()
        print("Account's balances must be cleared before removal.")
        return
   
    console.clear_screen()
    confirmation = input(f"Confirm removal of account {account.name} (Y/N): ").upper()

    if confirmation == "Y":   
        try:
            account_service.remove_account(conn, account.id)
            console.clear_screen()
            print(f"Account {account.name} removed successfully.")
        except Exception as e:
            console.clear_screen()
            print(e)
    else:
        console.clear_screen()
        print("Removing account cancelled.")
        return

def view_balances(conn):
    console.clear_screen()

    accounts = account_service.get_accounts(conn)
    us_stocks = stock_service.get_stocks(conn, "US")
    eu_stocks = stock_service.get_stocks(conn, "EU")

    if not accounts:
        print("No accounts available.")
        return
    
    us_stocks_value = stock_service.get_total_value(us_stocks)
    eu_stocks_value = stock_service.get_total_value(eu_stocks)
    
    try:
        data = account_service.get_totals(accounts, us_stocks_value, eu_stocks_value)
    except Exception as e:
        console.clear_screen()
        print("Failed to load balances:", e)
        return

    if data["total_usd_eur"] is None:
        print("Could not retrieve USD data.")
    else:
        print(f"{'EUR Assets:':<20} {data['total_eur']:>12.2f} €")
        print(f"{'USD Assets:':<20} {data['total_usd']:>12.2f} $ ({data['total_usd_eur']:>.2f} €)")
        print(f"{'Total Assets:':<20} {data['grand_total']:>12.2f} €")

    print("")
    print("Cash Assets:")

    for account in accounts:
        print(account)

    print("")
    print("Stock Assets:")
    
    print(f"{'EUR Value:' :<20} {eu_stocks_value:>12.2f} €")
    print(f"{'USD Value:' :<20} {us_stocks_value:>12.2f} $")

    input("Press enter to continue...")
    console.clear_screen()