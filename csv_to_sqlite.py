#!/usr/bin/env python3

# MADE WITH CODEIUM (CHATGPT)
import csv
import sqlite3
import sys
import os


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <database file> <csv file>")
        sys.exit(1)

    db_file = sys.argv[1]
    csv_file = sys.argv[2]

    # Determine table name from CSV file basename
    table_name = os.path.splitext(os.path.basename(csv_file))[0]

    # Open CSV file and read header and rows
    with open(csv_file, newline='') as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            print("CSV file is empty")
            sys.exit(1)
        # Assume header contains valid SQL column names
        columns = header
        rows = list(reader)

    # Create SQLite database connection
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()

    # Drop table if exists, then create new table
    cur.execute(f"DROP TABLE IF EXISTS {table_name}")
    # Build create table statement with columns assumed to be TEXT
    col_defs = ', '.join([f'"{col}" TEXT' for col in columns])
    create_stmt = f"CREATE TABLE {table_name} ({col_defs})"
    cur.execute(create_stmt)

    # Prepare insert statement
    placeholders = ', '.join(['?'] * len(columns))
    insert_stmt = f"INSERT INTO {table_name} VALUES ({placeholders})"

    # Insert all rows
    cur.executemany(insert_stmt, rows)

    # Commit changes and close the connection
    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()
