import utils.console as console
import services.account_service as account_service
import services.transaction_service as transaction_service
from models.transaction import Transaction
from datetime import datetime, date
import utils.formatting as formatting
import services.goal_service as goal_service
from decimal import Decimal
from models.goal import Goal, GoalScope, GoalPeriod

def insights_menu_loop(conn):
    console.clear_screen()
    while True:
        print("1. View Statistics")
        print("2. Add/Overwrite Goals")
        print("0. Main Menu")
        response = input("Select your option: ")
        match response:
            case "1":
                console.clear_screen()
                statistics_ui(conn)
            case "2":
                console.clear_screen()
                add_goals_ui(conn)
            case "0":
                console.clear_screen()
                break
            case _:
                console.clear_screen()
                print("Incorrect input. Please enter a number between 0 and 3.")
                continue

def add_goals_ui(conn):
    if goal_service.has_portfolio_goal(conn):
        print("Goals have already been set.")
        response = input("Would you like to overwrite these? (Y/N): ").capitalize()
        if response != "Y":
            console.clear_screen()
            return

    console.clear_screen()
    start_date = date.today()
    deadline_year_input = input("Enter year of the portfolio deadline: ")
    deadline_month_input = input("Enter month of the portfolio deadline (1-12): ")
    try:
        deadline = goal_service.validate_deadline(deadline_month_input, deadline_year_input, start_date)
    except ValueError as e:
        console.clear_screen()
        print(e)
        return

    accounts = account_service.get_cash_accounts(conn)
    account_goals = []

    for account in accounts:
        currency = "$" if account.currency == "USD" else "€"

        try:
            target_amount = Decimal(input(f"Enter target amount for account {account.name} ({currency}): "))
        except Exception:
            console.clear_screen()
            print("Invalid input")
            return
        account_goals.append({"account_id": account.id, "target": target_amount})

    try:
        goal_service.add_goals(conn, account_goals, start_date, deadline)
        console.clear_screen()
        print("Goals were added successfully!")
    except Exception as e:
        print(e)

def statistics_ui(conn):
    
    accounts = account_service.get_cash_accounts(conn)

    if not accounts:
        print("No accounts available.")
        return
    
    if not goal_service.has_portfolio_goal(conn):
        print("Statistics are not available. Goals have not yet been added.")
        return
    
    year = datetime.now().year
    month = datetime.now().month

    monthly_actual = transaction_service.get_totals(conn, accounts, year, month)
    yearly_actual = transaction_service.get_totals(conn, accounts, year)
    total_actual = transaction_service.get_totals(conn, accounts)

    deadline = goal_service.get_portfolio_deadline(conn)
    print(f"\nDeadline is {deadline}")

    for account in accounts:
        print_progress(
            conn,
            monthly_actual,
            yearly_actual,
            total_actual,
            account
            )
    
    print_progress(conn, monthly_actual, yearly_actual, total_actual)

    input("Press Enter to continue...")
    console.clear_screen()

def print_progress(
        conn,
        monthly_actual,
        yearly_actual,
        total_actual,
        account=None
    ):

    if account:
        total_target = goal_service.get_goal(conn, GoalPeriod.TOTAL, account.id).target_amount
        annual_target = goal_service.get_goal(conn, GoalPeriod.ANNUAL, account.id).target_amount
        monthly_target = goal_service.get_goal(conn, GoalPeriod.MONTHLY, account.id).target_amount

        name = account.name
        currency = "$" if account.currency == "USD" else "€"

    else:
        total_target = goal_service.get_goal(conn, GoalPeriod.TOTAL).target_amount
        annual_target = goal_service.get_goal(conn, GoalPeriod.ANNUAL).target_amount
        monthly_target = goal_service.get_goal(conn, GoalPeriod.MONTHLY).target_amount

        name = "Grand Total"
        currency = "€"

    month_progress = goal_service.calculate_progress(monthly_actual[name], monthly_target) if monthly_target else None
    year_progress = goal_service.calculate_progress(yearly_actual[name], annual_target) if annual_target else None
    total_progress = goal_service.calculate_progress(total_actual[name], total_target) if total_target else None

    month_goal_text = formatting.format_currency(monthly_target, currency) if monthly_target else "-"
    month_progress_text = f"{month_progress:.1f}%" if monthly_target else "-"
    year_goal_text = formatting.format_currency(annual_target, currency) if annual_target else "-"
    year_progress_text = f"{year_progress:.1f}%" if annual_target else "-"
    total_goal_text = formatting.format_currency(total_target, currency) if total_target else "-"
    total_progress_text = f"{total_progress:.1f}%" if total_target else "-"

    print(f"\n{name}")

    print(
        f"{'Period':<8}"
        f"{'Actual':>15}"
        f"{'Goal':>15}"
        f"{'Progress':>12}"
    )

    print(
        f"{'Month':<8}"
        f"{formatting.format_currency(monthly_actual[name], currency):>15}"
        f"{month_goal_text:>15}"
        f"{month_progress_text:>12}"
    )

    print(
        f"{'Year':<8}"
        f"{formatting.format_currency(yearly_actual[name], currency):>15}"
        f"{year_goal_text:>15}"
        f"{year_progress_text:>12}"
    )

    print(
        f"{'Total':<8}"
        f"{formatting.format_currency(total_actual[name], currency):>15}"
        f"{total_goal_text:>15}"
        f"{total_progress_text:>12}"
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