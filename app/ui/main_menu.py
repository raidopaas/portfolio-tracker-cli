import ui.account_ui as account_ui
#import ui.stock_ui as stock_ui
#import services.system_service as system_service
#import ui.account_ui as account_ui
#import ui.transaction_ui as transaction_ui
#import ui.stock_ui as stock_ui
import utils.console as console
#import ui.goals_ui as goals_ui

def main_menu_loop(conn):
    while True:
        print("1. View Balance")
        print("2. View Transactions")
        print("3. View Stocks")
        print("4. Add Transaction")
        print("5. Financial Goals")
        print("6. Add/Remove Account")
        print("7. Reset Data")
        print("0. Exit Program")
        response = input("Enter your choice: ")
        match response:
            case "1":
                pass
                #account_ui.view_balances(conn)
            case "2":
                pass
                #transaction_ui.view_transactions(conn)
            case "3":
                pass
                #stock_ui.view_stocks(conn)
            case "4":
                pass
                #transaction_ui.add_transaction_menu_loop(conn)
            case "5":
                pass
                #goals_ui.goals_ui_menu_loop(conn)
            case "6":
                console.clear_screen()
                user_choice = input("Enter 1 to add account or enter 2 to remove account: ")
                if user_choice == "1":
                    account_ui.add_account_ui(conn)
                elif user_choice == "2":
                    pass
                    #account_ui.remove_account_ui(conn)
                else:
                    console.clear_screen()
                    print("Invalid input.")
                    continue
            case "7":
                console.clear_screen()
                #reset_data_ui(conn)
            case "0":
                console.clear_screen()
                print("Good-Bye")
                break
            case _:
                console.clear_screen()
                print("Incorrect input. Please enter a number between 0 and 7.")
                continue