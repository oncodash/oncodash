#!/usr/bin/env python3
import logging

def column_to_tables(targets, cur):

    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()
    logging.debug(tables)


    col2tab = {}
    for t in tables:
        table = t[0]
        logging.debug(table)

        q=f"SELECT p.name as columnName FROM sqlite_master m LEFT OUTER JOIN pragma_table_info((m.name)) p on m.name <> p.name WHERE m.name == \"{table}\" ORDER BY m.name, columnName;"
        logging.debug(q)
        cur.execute(q)

        columns = cur.fetchall()
        logging.debug(columns)

        for c in columns:
            column = c[0]
            if column in targets:
                if column in col2tab:
                    col2tab[column].append(table)
                else:
                    col2tab[column] = [table]

    return col2tab


if __name__ == "__main__":
    import argparse
    import sqlite3


    do = argparse.ArgumentParser(
        prog='Oncodash SQLite3 database Anonymizer',
        description='Alter Oncodash’s Django/SQLite3 database to anonymize out sensitive clinical data.')

    do.add_argument("--log-level",
        default="INFO",
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help="Configure the log level (default: %(default)s).",
    )

    do.add_argument("filename")

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

    logging.info("Find out which tables contains targetable columns...")
    targets = ["cohort_code", "sample_id", "samples", "sample"]
    col2tab = column_to_tables(targets, cur)
    logging.info(col2tab)

    logging.debug("Close database connection")
    con.close()
