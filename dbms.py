from io import TextIOWrapper
import json
import sys
import os
import time

LN_LINES = 2
LN_CREATED = 3
LN_UPDATED = 4
LN_TABLES = 5

def create_file(filename):
    with open(filename, "a") as f:
        content = {
            'lines': 6,
            'created': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            'updated': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            'tables': [],
        }

        f.write("META\n")
        for key, val in content.items():
            f.write(f'{key}: {val}\n')


def overwriteLine(file: TextIOWrapper, line_number, content=""):
    file.seek(0)
    lines = file.readlines()

    if 0 <= line_number - 1 < len(lines):
        lines[line_number - 1] = str(content) + '\n'
    else:
        raise IndexError("Line number out of range")

    file.seek(0)
    file.truncate()
    file.writelines(lines)
    file.flush()


def insertLine(file: TextIOWrapper, line_number, content=""):
    file.seek(0)
    lines = file.readlines()
    lines.insert(line_number - 1, str(content) + '\n')
    file.seek(0)
    file.truncate()
    file.writelines(lines)
    file.flush()


def appendLine(file: TextIOWrapper, content=""):
    file.seek(0, 2)
    file.write(content + '\n')
    file.flush()


def readLine(file: TextIOWrapper, line_number):
    file.seek(0)
    
    for i, line in enumerate(file, start=1):
        if i == line_number:
            return line.rstrip('\n')
    
    raise IndexError("Line number out of range")


def deleteLine(file, line_number):
    file.seek(0)
    lines = file.readlines()
    
    if 0 <= line_number - 1 < len(lines):
        del lines[line_number - 1]
    else:
        raise IndexError("Line number out of range")
    
    file.seek(0)
    file.truncate()
    file.writelines(lines)
    file.flush()


def getLinesFromMeta(file: TextIOWrapper):
    return int(readLine(file, LN_LINES).strip().split(": ")[1])

def updateLinesToMeta(file: TextIOWrapper, amount):
    num_lines = getLinesFromMeta(file)
    num_lines += amount
    overwriteLine(file, LN_LINES, f"lines: {num_lines}")

def updateUpdatedToMeta(file: TextIOWrapper):
    overwriteLine(file, LN_UPDATED, "updated: " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))


def getTablesFromMeta(file: TextIOWrapper):
    tables = readLine(file, LN_TABLES).strip().split(": ")[1]
    return json.loads(tables)

def addTableToMeta(file: TextIOWrapper, table_name, line_number):
    tables = getTablesFromMeta(file)

    # TODO: Fix these two lines
    # Don't use sorting
    tables.sort()
    tables.append([line_number, table_name])

    overwriteLine(file, LN_TABLES, f"tables: {json.dumps(tables)}")
 
def updateTablesToMeta(file: TextIOWrapper, table_name, amount):
    tables = getTablesFromMeta(file)

    table_line = float('inf')
    i = 0
    for line_number, name in tables:
        if table_name == name: 
            table_line = line_number
        else:
            if line_number > table_line:
                tables[i] = [line_number + amount, name]
        i += 1

    overwriteLine(file, LN_TABLES, f"tables: {json.dumps(tables)}")

def deleteTablesToMeta(file: TextIOWrapper, table_name):
    tables = getTablesFromMeta(file)

    for index, table in enumerate(tables):
        if table_name == table[1]:
            break
    del tables[index]

    overwriteLine(file, LN_TABLES, f"tables: {json.dumps(tables)}")

def addTable(file: TextIOWrapper, table_name):

    content = {
        'name': table_name,
        'created': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        'updated': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        'columns': [],
        'rows': 0,
    }
    # Add content to file
    appendLine(file, "\nTABLE")
    appendLine(file, "\n".join([f'{key}: {val}' for key, val in content.items()]))

    # Update meta data
    addTableToMeta(file, table_name, getLinesFromMeta(file) + 1)
    updateLinesToMeta(file, 7)
    updateUpdatedToMeta(file)

def addRowToTable(file: TextIOWrapper, table_name, row):
    tables = getTablesFromMeta(file)
    table_line_number = None
    for line_number, name in tables:
        if name == table_name:
            table_line_number = line_number
            break
    if not table_line_number:
        raise ValueError("Table not found")
    
    print(table_line_number + 5)
    rows = int(readLine(file, table_line_number + 5).strip().split(": ")[1])
    insertLine(file, table_line_number + rows + 6, row)
    overwriteLine(file, table_line_number + 5, f'rows: {rows + 1}')
    updateLinesToMeta(file, 1)
    updateTablesToMeta(file, table_name, 1)

def deleteTable(file: TextIOWrapper, table_name):
    tables = getTablesFromMeta(file)

    table_line = 0
    for table in tables:
        if table[1] == table_name:
            table_line = table[0]
            break

    i = 1
    while readLine(file, table_line) != "":
        deleteLine(file, table_line)
        i += 1
    deleteLine(file, table_line)

    updateTablesToMeta(file, table_name, -i)
    updateLinesToMeta(file, -i)
    deleteTablesToMeta(file, table_name)
    

os.remove("_temp.db")
file = ""
if len(sys.argv) == 1:  # no file selected
    print("using temporary in-memory database")
    file = "_temp.db"
else:
    file = sys.argv[1]

if not os.path.exists(file):
    create_file(file)

# with open(file, "r+") as f:
#     updateUpdatedToMeta(f)

#     addTable(f, "table 1")
#     addTable(f, "temp table")
#     addTable(f, "table 2")
#     addTable(f, "table 3")

#     addRowToTable(f, "table 2", "apple")
#     addRowToTable(f, "table 2", "oranges")
#     addRowToTable(f, "table 3", "banana")

#     deleteTable(f, "temp table")

#     f.seek(0)
#     print(f.read())

# f.close()


# if file == "_temp.db":
#     os.remove(file)

