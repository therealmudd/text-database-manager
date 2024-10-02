import text_database_manager as tbm
from lexer import CustomLexer, PromptSession, style
import sys
import os
from tabulate import tabulate

filename = ""
if len(sys.argv) == 1:  # no file selected
    print("Using temporary in-memory database.")
    filename = "_temp.db"
else:
    filename = sys.argv[1]

# Initialize the database connection
try:
    db = tbm.TextDatabase(filename)
except Exception as e:
    print(f"Error initializing database: {e}")
    sys.exit(1)

help_text = \
'''tables \t\t\t\t views all tables
create <table> with <columns> \t creates table with columns
view <table> \t\t\t views all rows in table
delete <table> \t\t\t deletes table
insert <row> into <table> \t inserts row into table
remove <row> from <table> \t removes row from table
quit \t\t\t\t exits the program'''

session = PromptSession(lexer=CustomLexer({'help', 'tables', 'create', 'view', 'delete', 'insert', 'into', 'quit', 'with', 'remove', 'from'}), style=style)

while True:
    try:
        command_line = session.prompt("db> ").strip()
        command, *args = command_line.split()
    except Exception as e:
        print(f"Error processing command: {e}")
        continue

    if command == "help":
        print(help_text)

    elif command == "tables":
        try:
            tables = db.list_tables()
            print(tables)
        except Exception as e:
            print(f"Error listing tables: {e}")

    elif command == "create":
        if len(args) < 3 or args[1] != "with":
            print("Usage: create <table> with <columns>")
            continue

        table_name = args[0]
        columns = args[2:]

        try:
            if db.check_table_exists(table_name):
                print("Table already exists.")
            else:
                db.add_table(table_name, columns)
                print(f"Table '{table_name}' created successfully.")
        except Exception as e:
            print(f"Error creating table: {e}")

    elif command == "view":
        if not args:
            print("Usage: view <table>")
            continue

        table_name = args[0]
        try:
            if db.check_table_exists(table_name):
                table = db.view_table(table_name)
                if table:
                    print(tabulate(table[1:], headers=table[0]))
                else:
                    print("Table is empty.")
            else:
                print("Table does not exist.")
        except Exception as e:
            print(f"Error viewing table: {e}")

    elif command == "delete":
        if not args:
            print("Usage: delete <table>")
            continue

        table_name = args[0]
        try:
            if db.check_table_exists(table_name):
                db.delete_table(table_name)
                print(f"Table '{table_name}' deleted successfully.")
            else:
                print("Table does not exist.")
        except Exception as e:
            print(f"Error deleting table: {e}")

    elif command == "insert":
        if len(args) < 3 or args[1] != "into":
            print("Usage: insert <row> into <table>")
            continue

        row_data = args[0]
        table_name = args[2]
        
        try:
            if db.check_table_exists(table_name):
                db.add_row_to_table(table_name, row_data)
                print(f"Row inserted into table '{table_name}'.")
            else:
                print("Table does not exist.")
        except Exception as e:
            print(f"Error inserting row: {e}")

    elif command == "remove":
        if len(args) < 3 or args[1] != "from":
            print("Usage: remove <row> from <table>")
            continue

        row_data = args[0]
        table_name = args[2]
        
        try:
            if db.check_table_exists(table_name):
                db.delete_row_from_table(table_name, row_data)
                print(f"Row removed from table '{table_name}'.")
            else:
                print("Table does not exist.")
        except Exception as e:
            print(f"Error removing row: {e}")

    elif command == "quit":
        print("Exiting...")
        break

    else:
        print(f"Unknown command: {command}")

# Optional: Read the file if it exists and print its content
if os.path.exists(filename):
    try:
        with open(filename, "r") as file:
            print(file.read())
    except Exception as e:
        print(f"Error reading file '{filename}': {e}")
