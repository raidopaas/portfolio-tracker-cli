import utils.console as console
from decimal import Decimal, InvalidOperation
import services.stock_service as stock_service
import services.account_service as account_service
import ui.helpers as helpers
import utils.validation as validation
import services.transaction_service as transaction_service
import utils.formatting as formatting

def add_transaction_menu_loop(conn):
    console.clear_screen()
    while True:
        print("1. Deposit")
        print("2. Withdraw")
        print("3. Transfer")
        print("4. Buy Stocks")
        print("5. Sell Stocks")
        print("6. Update Stocks")
        print("0. Main Menu")
        response = input("Select your transaction: ")
        match response:
            case "1":
                console.clear_screen()
                deposit_ui(conn)
            case "2":
                console.clear_screen()
                withdraw_ui(conn)
            case "3":
                console.clear_screen()
                transfer_ui(conn)
            case "4":
                console.clear_screen()
                buy_stock_ui(conn)
            case "5":
                console.clear_screen()
                sell_stock_ui(conn)
            case "6":
                console.clear_screen()
                update_stocks_ui(conn)
            case "0":
                console.clear_screen()
                break
            case _:
                console.clear_screen()
                print("Incorrect input. Please enter a number between 0 and 6.")
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
    except Exception:
        console.clear_screen()
        print("Invalid input. Transaction cancelled.")
        return
    
    try:
        account_service.deposit(conn, account, amount, description)
        console.clear_screen()
        print(f"Deposit successful, {formatting.format_currency(amount, account.currency)} deposited to account {account.name}.")
    except Exception as e:
        console.clear_screen()
        print(e)

def withdraw_ui(conn):
    try:
        account = helpers.select_account(conn, transaction="withdraw")
    except Exception as e:
        console.clear_screen()
        print(e)
        return

    try:
        print(f"Account {account.name} balance is {account.balance} {account.currency}.")
        amount = Decimal(input(f"Enter withdrawal amount ({account.currency}): "))
        description = input("Enter description: ")
    except Exception:
        console.clear_screen()
        print("Invalid input. Transaction cancelled.")
        return
    
    try:
        account_service.withdraw(conn, account, amount, description)
        console.clear_screen()
        print(f"Withdrawal successful, {formatting.format_currency(amount, account.currency)} withdrawn from account {account.name}.")
    except Exception as e:
        console.clear_screen()
        print(e)

def transfer_ui(conn):
    try:
        account_from = helpers.select_account(conn, "transfer from")
    except Exception as e:
        console.clear_screen()
        print(e)
        return
    
    try:
        print(f"Account {account_from.name} balance is {account_from.balance} {account_from.currency}.")
        amount = Decimal(input(f"Enter transfer amount ({account_from.currency}): "))
    except Exception:
        console.clear_screen()
        print("Invalid input. Transaction cancelled.")
        return
    
    try:
        account_to = helpers.select_account(conn, "transfer to", exclude_account=[account_from.id])
    except Exception as e:
        console.clear_screen()
        print(e)
        return
    
    try:
        description_to = f"Transfer from {account_from.name} account."
        description_from = f"Transfer to {account_to.name} account."
        account_service.transfer(conn, account_from, account_to, amount, description_from, description_to)
        console.clear_screen()
        print(f"Transfer successful, {formatting.format_currency(amount, account_from.currency)} transferred from {account_from.name} account to {account_to.name} account.")
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
    
def sell_stock_ui(conn):
    market = input("Enter stock market for the transaction (US/EU): ").upper()
    if market in {"US", "EU"}:
        try:
            symbol = input("Enter stock symbol to sell: ").upper()
            current_qty = stock_service.get_stock_qty(conn, symbol)

            console.clear_screen()
            print(f"The balance of stock {symbol} is {current_qty} shares.")
            qty = int(input("Enter a number of shares to sell: "))

            price = None
            dividend = None

            if market == "EU":
                price = Decimal(input("Enter current stock price: "))
                dividend = Decimal(input("Enter current dividend: "))

        except Exception as e:
            console.clear_screen()
            print(e)
            return

        try:            
            stock_service.sell_stock(conn, market, symbol, qty, current_qty, price, dividend)
            console.clear_screen()
            print(f"Transaction succeeded. {qty} share(s) of {symbol} has been sold.")
        except Exception as e:
            console.clear_screen()
            print(e)
    else:
        console.clear_screen()
        print("Invalid input. Transaction cancelled.")
        return
    
def update_stocks_ui(conn):
    eu_stocks = stock_service.get_stocks(conn, "EU")

    manual_updates = {}

    for stock in eu_stocks:
        console.clear_screen()
        symbol = stock.symbol

        print(f"\nUpdating {symbol} (EU)")

        try:
            price = Decimal(input("Enter current price: "))
            dividend = Decimal(input("Enter current dividend: "))
        except InvalidOperation:
            console.clear_screen()
            print("Invalid input. Skipping this stock.")
            continue

        manual_updates[symbol] = {
            "price": price,
            "dividend": dividend
        }

    update_all = True if manual_updates else False

    try:
        stock_service.update_stocks(conn, update_all, manual_updates=manual_updates)
    except Exception as e:
        console.clear_screen()
        print(e)
        return

    console.clear_screen()
    print("Stocks updated succesfully!")
    
def view_transactions(conn):
    console.clear_screen()
    transactions = None

    try:
        account = helpers.select_account(conn, transaction="transactions list")
    except Exception as e:
        console.clear_screen()
        print(e)
        return
        
    user_input = input(
        "Do you want to see all the transactions history (Y/N): "
    ).upper()

    if user_input != "Y":
        print("Enter year and month of the transactions to view.")
        year = input("Enter year: ")
        month = input("Enter month (1-12): ")

        try:
            year = int(year)
            month = int(month)

            if not validation.is_valid_month(month):
                raise ValueError

        except ValueError:
            console.clear_screen()
            print("Invalid input")
            return
    else:
        year = None
        month = None

    try:
        transactions = transaction_service.get_transactions_for_account(conn, account.id, year, month)
    except ValueError as e:
        console.clear_screen()
        print(e)
        return

    if transactions:
        console.clear_screen()
        print_transactions(account.name, transactions)
        input("Press Enter to continue...")
        console.clear_screen()

    else:
        console.clear_screen()
        print("No transactions found.")

def print_transactions(account_name, transactions):
    print(f"Transactions for account {account_name}:")
    print(f"{'Amount':>14}   {'Date':<12}   Description")
    for transaction in transactions:
        print(transaction)