import json
import os
import time
from io import TextIOWrapper
import sys

LN_LINES = 2
LN_CREATED = 3
LN_UPDATED = 4
LN_TABLES = 5

class TextDatabase:
    def __init__(self, filename):
        self.filename = filename
        if not os.path.exists(filename):
            self.create_file()
        self.update_meta()

    def create_file(self):
        try:
            with open(self.filename, "a") as f:
                content = {
                    'lines': 6,
                    'created': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                    'updated': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                    'tables': [],
                }
                f.write("META\n")
                for key, val in content.items():
                    f.write(f'{key}: {val}\n')
        except Exception as e:
            print(f"Error creating file: {e}")

    def update_meta(self):
        try:
            with open(self.filename, "r+") as f:
                self.update_updated_to_meta(f)
        except Exception as e:
            print(f"Error updating meta: {e}")

    def update_updated_to_meta(self, file):
        self.overwrite_line(file, LN_UPDATED, "updated: " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    def overwrite_line(self, file: TextIOWrapper, line_number, content=""):
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

    def insert_line(self, file: TextIOWrapper, line_number, content=""):
        file.seek(0)
        lines = file.readlines()
        lines.insert(line_number - 1, str(content) + '\n')
        file.seek(0)
        file.truncate()
        file.writelines(lines)
        file.flush()

    def append_line(self, file: TextIOWrapper, content=""):
        file.seek(0, 2)
        file.write(content + '\n')
        file.flush()

    def read_line(self, file: TextIOWrapper, line_number):
        file.seek(0)

        for i, line in enumerate(file, start=1):
            if i == line_number:
                return line.rstrip('\n')

        raise IndexError("Line number out of range")

    def delete_line(self, file, line_number):
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

    def get_lines_from_meta(self, file: TextIOWrapper):
        return int(self.read_line(file, LN_LINES).strip().split(": ")[1])

    def update_lines_to_meta(self, file: TextIOWrapper, amount):
        num_lines = self.get_lines_from_meta(file)
        num_lines += amount
        self.overwrite_line(file, LN_LINES, f"lines: {num_lines}")

    def get_tables_from_meta(self, file: TextIOWrapper):
        tables = self.read_line(file, LN_TABLES).strip().split(": ")[1]
        return json.loads(tables)

    def get_table_line_from_meta(self, file: TextIOWrapper, table_name):
        tables = self.get_tables_from_meta(file)
        for table in tables:
            if table[1] == table_name:
                return table[0]
        raise ValueError("Table not found")

    def get_table_line_from_list(self, tables, table_name):
        for table in tables:
            if table[1] == table_name:
                return table[0]
        raise ValueError("Table not found")

    def add_table_to_meta(self, file: TextIOWrapper, table_name, line_number):
        tables = self.get_tables_from_meta(file)
        tables.append([line_number, table_name])
        self.overwrite_line(file, LN_TABLES, f"tables: {json.dumps(tables)}")

    def update_tables_to_meta(self, file: TextIOWrapper, table_name, amount):
        tables = self.get_tables_from_meta(file)
        table_line = self.get_table_line_from_list(tables, table_name)

        if table_line is None:
            raise ValueError("Table not found in metadata")

        for i in range(len(tables)):
            if tables[i][0] > table_line:
                tables[i][0] += amount

        self.overwrite_line(file, LN_TABLES, f"tables: {json.dumps(tables)}")

    def delete_tables_to_meta(self, file: TextIOWrapper, table_name):
        tables = self.get_tables_from_meta(file)
        tables = [table for table in tables if table[1] != table_name]
        self.overwrite_line(file, LN_TABLES, f"tables: {json.dumps(tables)}")

    def add_table(self, table_name):
        with open(self.filename, "r+") as file:
            content = {
                'name': table_name,
                'created': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                'updated': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                'columns': [],
                'rows': 0,
            }
            lines_to_add = ["\nTABLE"] + [f'{key}: {val}' for key, val in content.items()]
            self.append_line(file, "\n".join(lines_to_add))

            self.add_table_to_meta(file, table_name, self.get_lines_from_meta(file) + 1)
            self.update_lines_to_meta(file, 7)
            self.update_updated_to_meta(file)

    def update_table_updated(self, file, table_name):
        table_line_number = self.get_table_line_from_meta(file, table_name)
        self.overwrite_line(file, table_line_number + 3, f"updated: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
        self.update_updated_to_meta(file)

    def add_row_to_table(self, table_name, row):
        with open(self.filename, "r+") as file:
            table_line_number = self.get_table_line_from_meta(file, table_name)

            rows = int(self.read_line(file, table_line_number + 5).strip().split(": ")[1])
            self.insert_line(file, table_line_number + rows + 6, row)
            self.overwrite_line(file, table_line_number + 5, f'rows: {rows + 1}')
            self.update_lines_to_meta(file, 1)
            self.update_tables_to_meta(file, table_name, 1)
            self.update_updated_to_meta(file)
            self.update_table_updated(file, table_name)
        
    def delete_row_from_table(self, table_name, row):
        with open(self.filename, "r+") as file:
            table_line_number = self.get_table_line_from_meta(file, table_name)

            rows = int(self.read_line(file, table_line_number + 5).strip().split(": ")[1])
            deleted_rows = 0
            i = rows
            while i > 0:
                row_number = table_line_number + 5 + i
                if self.read_line(file, row_number) == row:
                    self.delete_line(file, row_number)
                    self.update_lines_to_meta(file, -1)
                    deleted_rows += 1
                else:
                    i -= 1
            if deleted_rows:
                self.update_updated_to_meta(file)
                self.overwrite_line(file, table_line_number + 5, f'rows: {rows - deleted_rows}')
                self.update_table_updated(file, table_name)

    def delete_table(self, table_name):
        with open(self.filename, "r+") as file:
            tables = self.get_tables_from_meta(file)

            table_line = 0
            for table in tables:
                if table[1] == table_name:
                    table_line = table[0]
                    break

            i = 1
            while self.read_line(file, table_line) != "":
                self.delete_line(file, table_line)
                i += 1
            self.delete_line(file, table_line)

            self.update_tables_to_meta(file, table_name, -i)
            self.update_lines_to_meta(file, -i)
            self.delete_tables_to_meta(file, table_name)
            self.update_updated_to_meta(file)

# Main execution
def main():
    if os.path.exists("_temp.db"):
        os.remove("_temp.db")
    file = "_temp.db"

    db = TextDatabase(file)

    db.add_table("table 1")
    db.add_table("temp table")
    db.add_table("table 2")
    db.add_table("table 3")

    db.add_row_to_table("table 2", "apple")
    db.add_row_to_table("table 2", "oranges")
    db.add_row_to_table("table 3", "banana")
    db.add_row_to_table("table 1", "temp row")
    db.add_row_to_table("table 1", "temp row")
    db.add_row_to_table("table 1", "temp row")

    db.delete_table("temp table")

    time.sleep(1)

    db.delete_row_from_table("table 1", "temp row")

    with open(file, "r") as f:
        print(f.read())

    # if file == "_temp.db":
    #     os.remove(file)


if __name__ == "__main__":
    main()
