import utils.console as console
import services.account_service as account_service
import services.transaction_service as transaction_service
from models.transaction import Transaction
from datetime import datetime
import utils.formatting as formatting
import ui.goal_ui as goal_ui

def insights_menu_loop(conn):
    console.clear_screen()
    while True:
        print("1. View Statistics")
        print("2. View Progress")
        print("3. Add/Remove/Modify Goals")
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
                goal_ui.goals_menu_loop(conn)
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
    month = datetime.now().month

    totals_month = transaction_service.get_totals(conn, accounts, year, month)
    totals_year = transaction_service.get_totals(conn, accounts, year)
    
    print("Progress:\n")
    print_totals(accounts, totals_month, totals_year)

    input("Press Enter to continue...")
    console.clear_screen()

def print_totals(accounts, totals_month, totals_year):
    print(f"{'Account':<15} {'Month':>15} {'Year':>15}")
    for account in accounts:
        currency = "$" if account.currency == "USD" else "€"
        print(
            f"{account.name:<15} "
            f"{formatting.format_currency(totals_month[account.name], currency):>15} "
            f"{formatting.format_currency(totals_year[account.name], currency):>15}"
        )

    print("-" * 50)
    print(
        f"{'Grand Total':<15} "
        f"{formatting.format_currency(totals_month['Grand Total'], "€"):>15} "
        f"{formatting.format_currency(totals_year['Grand Total'], "€"):>15}"
    )