from db.connection import get_connection
import ui.cli as cli
#import test_api

conn = get_connection()

def main():
    #test_api.test_api()
    cli.begin_interaction(conn)

main()

conn.close()