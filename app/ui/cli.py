import utils.console as console
import ui.main_menu as main_menu

def begin_interaction(conn):
    console.clear_screen()
    print("Welcome to Finances Program")
    main_menu.main_menu_loop(conn)