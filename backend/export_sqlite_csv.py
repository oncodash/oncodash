#!/usr/bin/env python3

import re
import csv
import logging

if __name__ == "__main__":
    import argparse
    import sqlite3
    import os
    import sys

    do = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description="""Export the given tables of a SQLite3 database to CSV files.""",
        epilog=f"Example:\n\t./{os.path.basename(sys.argv[0])} db.sqlite3 --list-tables\n\t./{os.path.basename(sys.argv[0])} db.sqlite3 genomics_cgi[dm] genomics_oncokb --log-level INFO --prefix test_")

    do.add_argument("--log-level",
        default="INFO",
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help="Configure the log level (default: %(default)s).",
    )

    do.add_argument("-l", "--list-tables", action="store_true", help="List the available tables and exit.")

    do.add_argument("-p", "--prefix", type=str, default="", help="Prefix for naming the CSV file.")

    do.add_argument("filename", metavar="FILENAME", help="SQLite3 database file.")
    do.add_argument("tables", metavar="TABLE", nargs='+', help="Regular expression(s) matching the table names to export.")

    asked = do.parse_args()

    logging.basicConfig(level = asked.log_level)

    logging.info("Connect to the database...")
    try:
        con = sqlite3.connect(asked.filename)
        cur = con.cursor()
    except e:
        logging.error(e)
        exit(1)

    logging.debug("Connection OK")

    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [entry[0] for entry in cur.fetchall()]

    if asked.list_tables:
        print("\n".join(tables))
        exit(0)

    for table in tables:
        if any(re.match(asked_table, table) for asked_table in asked.tables):
            filename = f"{asked.prefix}{table}.csv"
            logging.info(f"Export '{table}' to '{filename}'...")
            data = cur.execute(f"SELECT * FROM {table}")
            columns = [d[0] for d in cur.description]
            with open(filename, 'w') as fd:
                writer = csv.writer(fd)
                writer.writerow(columns)
                writer.writerows(data)
            logging.debug("OK")

    logging.info("Done")
