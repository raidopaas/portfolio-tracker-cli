from db.connection import get_connection
import ui.cli as cli

conn = get_connection()

def main():
    cli.begin_interaction(conn)

main()

conn.close()