import utils.console as console
from models.goal import GoalScope, GoalPeriod
from datetime import datetime
import calendar
import services.goal_service as goal_service
from decimal import Decimal
import services.account_service as account_service

def goals_menu_loop(conn):
    console.clear_screen()
    while True:
        print("1. Add Goal")
        print("2. View Progress")
        print("3. Add/Remove/Modify Goals")
        print("4. Reset Goals")
        print("0. Main Menu")
        response = input("Select your option: ")
        match response:
            case "1":
                console.clear_screen()
                add_goal_ui(conn)
            case "4":
                console.clear_screen()
                try:
                    goal_service.reset_goals(conn)
                except Exception as e:
                    print(e)
                print("Goals have been reset.")
            case "0":
                console.clear_screen()
                break
            case _:
                console.clear_screen()
                print("Incorrect input. Please enter a number between 0 and 4.")
                continue

def add_goal_ui(conn):
    if goal_service.has_portfolio_goal(conn):
        print("Goals have already been set.")
        response = input("Would you like to overwrite these? (Y/N): ").capitalize()
        if response != "Y":
            console.clear_screen()
            return

    console.clear_screen()
    goal_service.reset_goals(conn)
    deadline_input = input("Enter portfolio deadline (YYYY-MM-DD): ")
    try:
        deadline = datetime.strptime(deadline_input, "%Y-%m-%d").date()
    except ValueError:
        console.clear_screen()
        print("Invalid date input")
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
            goal_service.add_goal(conn, target_amount, deadline, GoalScope.ACCOUNT, GoalPeriod.TOTAL, account.id)
            goal_service.add_account_mid_goals(conn, target_amount, deadline, account.id)
            console.clear_screen()
            print(f"Account {account.name} total goal added succesfully.")
        except Exception as e:
            console.clear_screen()
            print("Adding new goal failed", e)
            return
        
    try:
        goal_service.add_goal(conn, end_target, deadline, GoalScope.PORTFOLIO, GoalPeriod.TOTAL)
        console.clear_screen()
        print(f"Portfolio goal {end_target}€, {deadline} added succesfully.")
    except Exception as e:
        console.clear_screen()
        print("Adding new goal failed", e)
        return
    
    goal_service.add_mid_goals(conn, end_target, deadline)