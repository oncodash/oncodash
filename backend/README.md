# Oncodash Back-end

The oncodash back-end is used to serve API-endpoints for the front-end application


# Tools

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

