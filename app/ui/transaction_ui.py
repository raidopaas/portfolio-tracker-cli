import utils.console as console
from decimal import Decimal
import services.stock_service as stock_service
import services.account_service as account_service
import ui.helpers as helpers

def add_transaction_menu_loop(conn):
    console.clear_screen()
    while True:
        print("1. Deposit")
        print("2. Withdraw")
        print("3. Buy Stocks")
        print("4. Sell Stocks")
        print("5. Update Stocks")
        print("0. Main Menu")
        response = input("Select your transaction: ")
        match response:
            case "1":
                console.clear_screen()
                deposit_ui(conn)
            case "2":
                pass
            case "3":
                console.clear_screen()
                buy_stock_ui(conn)
            case "4":
                pass
            case "5":
                pass
            case "0":
                console.clear_screen()
                break
            case _:
                console.clear_screen()
                print("Incorrect input. Please enter a number between 0 and 5.")
                continue

def deposit_ui(conn):
    try:
        account = helpers.select_account(conn, transaction="deposit")
    except Exception as e:
        console.clear_screen()
        print(e)
        return
    try:
        amount = Decimal(input(f"Enter deposit amount ({account.currency}): "))
        description = input("Enter description: ")
    except Exception as e:
        console.clear_screen()
        print("Invalid input. Transaction cancelled.")
        return
    
    try:
        account_service.deposit(conn, account.id, amount, description)
        console.clear_screen()
        print(f"Deposit successful, {amount} {account.currency} deposited to account {account.name}.")
    except Exception as e:
        console.clear_screen()
        print(e)

def buy_stock_ui(conn):
    market = input("Enter stock market from where to buy (US/EU): ").upper()
    if market in {"US", "EU"}:
        try:
            symbol = input("Enter stock symbol to buy: ").upper()
            qty = int(input("Enter quantity: "))
            price = None
            dividend = None
            if market == "EU":
                price = Decimal(input("Enter current stock price: "))
                dividend = Decimal(input("Enter current dividend: "))
        except Exception:
            console.clear_screen()
            print("Invalid input. Transaction cancelled.")
            return

        try:
            stock_service.buy_stock(conn, market, symbol, qty, price, dividend)
            console.clear_screen()
            print(f"Transaction succeeded. {qty} share of {symbol} has been purchased.")
        except Exception as e:
            console.clear_screen()
            print(e)
    else:
        console.clear_screen()
        print("Invalid input. Transaction cancelled.")
        return