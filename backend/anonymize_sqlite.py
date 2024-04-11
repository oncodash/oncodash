#!/usr/bin/env python3

import re
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


def find_cohort_codes(col2tab, cur):
    queries = []
    for column in col2tab:
        for table in col2tab[column]:
            queries.append(f"SELECT {column} FROM {table}")
    query = " UNION ".join(queries)

    def find_cohort_code(value):
        m = re.search("^([A-Z][0-9]{3})_\w*.*$", value)
        if m:
            return m.group(1)
        elif re.match("^[A-Z][0-9]{3}$", value):
            return value
        else:
            return None

    cohort_codes = set()
    for v in cur.execute(query):
        value = v[0]
        if ";" in value: # Multiple values
            for val in value.split(";"):
                cc = find_cohort_code(val)
                if cc:
                    cohort_codes.add(cc)
        else:
            cc = find_cohort_code(value)
            if cc:
                cohort_codes.add(cc)

    return cohort_codes


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

    logging.info("Find out cohort codes...")
    cohort_codes = find_cohort_codes(col2tab, cur)
    logging.debug(cohort_codes)

    logging.debug("Close database connection")
    con.close()
