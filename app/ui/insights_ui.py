import utils.console as console
import services.account_service as account_service
import services.transaction_service as transaction_service
from models.transaction import Transaction
from datetime import datetime
import utils.formatting as formatting
import ui.goal_ui as goal_ui
import services.goal_service as goal_service

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
                #view_progress(conn)
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
    if not goal_service.has_portfolio_goal(conn):
        print("Goals have not been set up.")
        return
    
    accounts = account_service.get_accounts(conn)
    year = datetime.now().year
    month = datetime.now().month

    monthly_actual = transaction_service.get_totals(conn, accounts, year, month)
    yearly_actual = transaction_service.get_totals(conn, accounts, year)
    total_actual = transaction_service.get_totals(conn, accounts)

    for account in accounts:
        print_account_progress(
            conn, 
            account, 
            monthly_actual,
            yearly_actual,
            total_actual
            )
    
    print_grand_total_progress(conn, monthly_actual, yearly_actual, total_actual)

    input("Press Enter to continue...")
    console.clear_screen()

def print_account_progress(
        conn,
        account,
        monthly_actual,
        yearly_actual,
        total_actual
):
    goals = goal_service.get_account_goals(conn, account.id)

    monthly_goal = goals["monthly"]
    yearly_goal = goals["yearly"]
    total_goal = goals["total"]

    month_progress = goal_service.calculate_progress(monthly_actual[account.name], monthly_goal.target_amount)
    year_progress = goal_service.calculate_progress(yearly_actual[account.name], yearly_goal.target_amount)
    total_progress = goal_service.calculate_progress(total_actual[account.name], total_goal.target_amount)

    currency = "$" if account.currency == "USD" else "€"

    print(f"\n{account.name}")

    print(
        f"{'Period':<8}"
        f"{'Actual':>15}"
        f"{'Goal':>15}"
        f"{'Progress':>12}"
    )

    print(
        f"{'Month':<8}"
        f"{formatting.format_currency(monthly_actual[account.name], currency):>15}"
        f"{formatting.format_currency(monthly_goal.target_amount, currency):>15}"
        f"{month_progress:>11.1f}%"
    )

    print(
        f"{'Year':<8}"
        f"{formatting.format_currency(yearly_actual[account.name], currency):>15}"
        f"{formatting.format_currency(yearly_goal.target_amount, currency):>15}"
        f"{year_progress:>11.1f}%"
    )

    print(
        f"{'Total':<8}"
        f"{formatting.format_currency(total_actual[account.name], currency):>15}"
        f"{formatting.format_currency(total_goal.target_amount, currency):>15}"
        f"{total_progress:>11.1f}%"
    )

def print_grand_total_progress(conn, monthly_actual, yearly_actual, total_actual):
    goals = goal_service.get_portfolio_goals(conn)
    
    monthly_goal = goals["monthly"]
    yearly_goal = goals["yearly"]
    total_goal = goals["total"]

    month_progress = goal_service.calculate_progress(monthly_actual['Grand Total'], monthly_goal.target_amount)
    year_progress = goal_service.calculate_progress(yearly_actual['Grand Total'], yearly_goal.target_amount)
    total_progress = goal_service.calculate_progress(total_actual['Grand Total'], total_goal.target_amount)

    currency = "€"

    print("\nGrand Total")

    print(
        f"{'Period':<8}"
        f"{'Actual':>15}"
        f"{'Goal':>15}"
        f"{'Progress':>12}"
    )

    print(
        f"{'Month':<8}"
        f"{formatting.format_currency(monthly_actual['Grand Total'], currency):>15}"
        f"{formatting.format_currency(monthly_goal.target_amount, currency):>15}"
        f"{month_progress:>11.1f}%"
    )

    print(
        f"{'Year':<8}"
        f"{formatting.format_currency(yearly_actual['Grand Total'], currency):>15}"
        f"{formatting.format_currency(yearly_goal.target_amount, currency):>15}"
        f"{year_progress:>11.1f}%"
    )

    print(
        f"{'Total':<8}"
        f"{formatting.format_currency(total_actual['Grand Total'], currency):>15}"
        f"{formatting.format_currency(total_goal.target_amount, currency):>15}"
        f"{total_progress:>11.1f}%"
    )
    
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