import utils.console as console
import services.account_service as account_service
import services.transaction_service as transaction_service
from models.transaction import Transaction
from datetime import datetime

def insights_menu_loop(conn):
    console.clear_screen()
    while True:
        print("1. View Statistics")
        print("2. View Progress")
        print("3. Add/Remove Goal")
        print("0. Main Menu")
        response = input("Select your option: ")
        match response:
            case "1":
                console.clear_screen()
                statistics_ui(conn)
            case "2":
                console.clear_screen()
                #withdraw_ui(conn)
            case "3":
                console.clear_screen()
                #transfer_ui(conn)
            case "0":
                console.clear_screen()
                break
            case _:
                console.clear_screen()
                print("Incorrect input. Please enter a number between 0 and 3.")
                continue

def statistics_ui(conn):
    accounts = account_service.get_accounts(conn)
    year = datetime.now().year
    account_transactions = {}
    account_number = 0

    for acc in accounts:
        account_transactions[acc.name] = transaction_service.get_transactions_for_account(conn, acc.id, year, month=None)
        for transaction in account_transactions[acc.name]:
            print(transaction)
        input("Press Enter to continue...")
        account_number += 1
    
