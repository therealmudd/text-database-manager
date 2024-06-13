import text_database_manager as tbm
from lexer import CustomLexer, PromptSession, style
import sys
import os

filename = ""
if len(sys.argv) == 1:  # no file selected
    print("using temporary in-memory database")
    filename = "_temp.db"
else:
    filename = sys.argv[1]

db = tbm.TextDatabase(filename)

help_text = \
'''tables \t\t\t\t views all tables
create <table> with <columns> \t creates table with columns
view <table> \t\t\t views all rows in table
delete <table> \t\t\t deletes table
insert <row> into <table> \t inserts row into table
quit \t\t\t\t exits the program'''

#session = PromptSession(lexer=CustomLexer({'help', 'tables', 'create', 'view', 'delete', 'insert', 'into', 'quit', 'with'}), style=style)
while True:
    command, *args = input("db> ").strip().split() #session.prompt("db> ").strip().split()

    if command == "help":
        print(help_text)
    elif command == "tables":
        print(db.list_tables())
    elif command == "create":
        if len(args) < 3: 
            print("Usage: create <table> with <columns>")
        elif db.check_table_exists(args[0]):
            print("Table already exists")
        else:
            db.add_table(args[0], args[2])

    elif command == "view":
        if db.check_table_exists(args[0]):
            print(db.view_table(args[0]))
        else:
            print("Table does not exist")

    elif command == "delete":
        if db.check_table_exists(args[0]):
            db.delete_table(args[0])
        else:
            print("Table does not exist")
    
    elif command == "insert":
        db.add_row_to_table(args[2], args[0])

    elif command == "quit":
        break

with open(filename, "r") as file:
    print(file.read())
