#!/usr/bin/env python3

import re
import string
import random
import logging

def unfold(list_of_tuples, sep=", "):
    return sep.join(v[0] for v in list_of_tuples)


def column_to_tables(targets, cur):
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()

    col2tab = {}
    for t in tables:
        table = t[0]
        logging.debug(f"\t{table}")

        q=f"SELECT p.name as columnName FROM sqlite_master m LEFT OUTER JOIN pragma_table_info((m.name)) p on m.name <> p.name WHERE m.name == \"{table}\" ORDER BY m.name, columnName;"
        cur.execute(q)

        columns = cur.fetchall()

        for c in columns:
            column = c[0]
            if column in targets:
                logging.debug(f"\t\t{column}")
                if column in col2tab:
                    col2tab[column].append(table)
                else:
                    col2tab[column] = [table]

    return col2tab


def find_cohort_code(value):
    m = re.search("^([A-Z]{1,2}[0-9]{3})_\w*.*$", value)
    if m:
        return m.group(1)
    elif re.match("^[A-Z]{1,2}[0-9]{3}$", value):
        return value
    else:
        return None

def find_cohort_codes(col2tab, cur):
    queries = []
    for column in col2tab:
        for table in col2tab[column]:
            queries.append(f"SELECT {column} FROM {table}")
    query = " UNION ".join(queries)

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


def anonymize_value(value, anon_map):
    assert(";" not in value)
    value = re.sub("_DNA[1-2]*$", "", value)
    m = re.search("^([A-Z]{1,2}[0-9]{3})", value)
    if m:
        code = m.group(1)
        return re.sub(code, anon_map[code], value)
    else:
        return None

def anonymize_all(col2tab, cur):
    for column in col2tab:
        logging.info(f"\t{column}")
        for table in col2tab[column]:
            # Long entries first, to avoid partial replacement.
            cur.execute(f"SELECT DISTINCT {column} FROM {table} ORDER BY length({column}) DESC;")
            values = cur.fetchall()
            logging.info(f"\t\t{table}")
            for v in values:
                value = v[0]
                if ";" in value:
                    vals = []
                    for val in value.split(";"):
                        new = anonymize_value(val, anon_map)
                        vals.append(new)
                    new_val = ";".join(vals)
                else:
                    new_val = anonymize_value(value, anon_map)

                if value and new_val:
                    # logging.debug(f"\t{value}\t=>\t{new_val}")
                    cur.execute(f"UPDATE {table} SET {column} = REPLACE({column}, '{value}', '{new_val}');")


if __name__ == "__main__":
    import argparse
    import sqlite3
    import os
    import sys

    do = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description="""Alter an Oncodash’s Django/SQLite3 database to anonymize out cohort and sample names.\n\nWARNING: does alter IN PLACE the database file, do not forget to make a backup first.""",
        epilog=f"Example:\n\t./{os.path.basename(sys.argv[0])} db.sqlite3 --targets cohort_code sample_id samples sample --log-level INFO")

    do.add_argument("--log-level",
        default="INFO",
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help="Configure the log level (default: %(default)s).",
    )

    do.add_argument('-t', '--targets', nargs='+', default=["cohort_code", "sample_id", "samples", "sample"],
        help="Columns names in which to anonymize cohort codes.")

    do.add_argument("filename", metavar="FILENAME")

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
    targets = asked.targets
    col2tab = column_to_tables(targets, cur)
    logging.debug("Columns to tables:")
    for col in col2tab:
        logging.debug(f"\t{col}")
        for tab in col2tab[col]:
            logging.debug(f"\t\t{tab}")

    logging.info("Find out cohort codes...")
    cohort_codes = find_cohort_codes(col2tab, cur)

    logging.info("Prepare anonymization mapping...")
    anon_map = {}
    for cc in cohort_codes:
        anon_map[cc] = "CC" + "".join(random.choices(string.digits, k=4))

    for cc in anon_map:
        logging.debug(f"\t{cc}\t=>\t{anon_map[cc]}")

    logging.info("Compute anonymization...")
    anonymize_all(col2tab, cur)

    logging.info("Apply anonymization...")
    con.commit()

    logging.info("Consistency checks...")
    for column in col2tab:
        for table in col2tab[column]:
            for v in cur.execute(f"SELECT DISTINCT {column} FROM {table};"):
                value = v[0]
                cc = find_cohort_code(value)
                if cc in anon_map:
                    logging.error(f"{cc} found in {column} of {table}: {value}")


    logging.debug("Close database connection...")
    con.close()
    logging.info("Done")
