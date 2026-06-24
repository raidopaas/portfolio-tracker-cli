import utils.console as console
import services.account_service as account_service
import services.transaction_service as transaction_service
from models.transaction import Transaction
from datetime import datetime
import utils.formatting as formatting
import app.services.insight_service as insight_service
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
                add_goal_ui(conn)
            case "0":
                console.clear_screen()
                break
            case _:
                console.clear_screen()
                print("Incorrect input. Please enter a number between 0 and 3.")
                continue

def statistics_ui(conn):
    
    accounts = account_service.get_cash_accounts(conn)
    year = datetime.now().year
    month = datetime.now().month

    monthly_actual = transaction_service.get_totals(conn, accounts, year, month)
    yearly_actual = transaction_service.get_totals(conn, accounts, year)
    total_actual = transaction_service.get_totals(conn, accounts)

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
        goals = insight_service.get_account_goals(conn, account.id)
        name = account.name
        currency = "$" if account.currency == "USD" else "€"
    else:
        goals = insight_service.get_portfolio_goals(conn)
        name = "Grand Total"
        currency = "€"

    monthly_goal = goals["monthly"]
    yearly_goal = goals["yearly"]
    total_goal = goals["total"]

    month_goal_amount = monthly_goal.target_amount if monthly_goal else None
    year_goal_amount = yearly_goal.target_amount if yearly_goal else None
    total_goal_amount = total_goal.target_amount if total_goal else None

    month_progress = insight_service.calculate_progress(monthly_actual[name], month_goal_amount) if month_goal_amount else None
    year_progress = insight_service.calculate_progress(yearly_actual[name], year_goal_amount) if year_goal_amount else None
    total_progress = insight_service.calculate_progress(total_actual[name], total_goal_amount) if total_goal_amount else None

    month_goal_text = formatting.format_currency(month_goal_amount, currency) if monthly_goal else "-"
    month_progress_text = f"{month_progress:.1f}%" if monthly_goal else "-"
    year_goal_text = formatting.format_currency(year_goal_amount, currency) if yearly_goal else "-"
    year_progress_text = f"{year_progress:.1f}%" if yearly_goal else "-"
    total_goal_text = formatting.format_currency(total_goal_amount, currency) if total_goal else "-"
    total_progress_text = f"{total_progress:.1f}%" if total_goal else "-"

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

def add_goal_ui(conn):
    if insight_service.has_portfolio_goal(conn):
        print("Goals have already been set.")
        response = input("Would you like to overwrite these? (Y/N): ").capitalize()
        if response != "Y":
            console.clear_screen()
            return

    console.clear_screen()
    insight_service.reset_goals(conn)
    deadline_year_input = input("Enter year of the portfolio deadline: ")
    deadline_month_input = input("Enter month of the portfolio deadline (1-12): ")
    try:
        deadline = insight_service.validate_deadline(deadline_month_input, deadline_year_input)
    except ValueError as e:
        console.clear_screen()
        print(e)
        return

    accounts = account_service.get_cash_accounts(conn)
    end_target = Decimal("0.00")

    for account in accounts:
        currency = "$" if account.currency == "USD" else "€"

        try:
            target_amount = Decimal(input(f"Enter target amount for account {account.name} ({currency}): "))
            end_target += target_amount
        except Exception:
            console.clear_screen()
            print("Invalid input")
            return
        try:
            insight_service.add_account_goal(conn, target_amount, GoalPeriod.TOTAL, account.id, deadline)
            insight_service.add_mid_goals(conn, target_amount, deadline, GoalScope.ACCOUNT, account.id)
            console.clear_screen()
            print(f"Account {account.name} goals added succesfully.")
        except Exception as e:
            console.clear_screen()
            print("Adding goals failed", e)
            return
        
    try:
        insight_service.add_portfolio_goal(conn, end_target, GoalPeriod.TOTAL, deadline)
        insight_service.add_mid_goals(conn, end_target, deadline, GoalScope.PORTFOLIO)
        console.clear_screen()
        print(f"Portfolio goal {end_target}€, {deadline} added succesfully.")
    except Exception as e:
        console.clear_screen()
        print("Adding new goal failed", e)
        return