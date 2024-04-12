# Oncodash Back-end

The oncodash back-end is used to serve API-endpoints for the front-end application


# Tools

## Export

The `export_sqlite_csp.py` script allows to export some tables to CSV files.

You can indicate which table you want using a matching regular expression.

For example:
```sh
./export_sqlite_csv.py db.sqlite3 genomics_cgi[dm] genomics_oncokb --log-level INFO --prefix test_
```

## Anonymization

The `anonymize_sqlite.py` script allows to alter an Oncodash’s Django/SQLite3
database to anonymize out cohort and sample names.

***WARNING***: does alter **IN PLACE** the database file, do not forget to make a **backup** first.

Usage:
```sh
./anonymize_sqlite.py db.sqlite3
```

which by default executes:
```sh
./anonymize_sqlite.py db.sqlite3 --targets cohort_code sample_id samples sample --log-level INFO
```

The script looks into everything looking like a cohort code (matching `[A-Z]{1,2}[0-9]{3}`)
in the given list of target columns, and replace them with randomly generated
codes.
It also removes any `_DNA[0-9]*` suffixe from sample IDs.

