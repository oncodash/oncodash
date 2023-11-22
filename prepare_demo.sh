#!/bin/bash

cases=("H115" "H243" "H266" "M035" "D351")

cnacsv=$1
snvcsv=$2
ascats=$3
oncokbatargets=$4

docker compose run --rm backend sh -c "python manage.py import_genomic_variants --copy_number_alterations ${cnacsv}"
docker compose run --rm backend sh -c "python manage.py import_genomic_variants --somatic_variants ${snvcsv}"
docker compose run --rm backend sh -c "python manage.py import_genomic_variants --ascatestimates ${ascats}"
docker compose run --rm backend sh -c "python manage.py import_genomic_variants --oncokb_actionable_targets ${oncokbatargets}"

mkdir -p ./tmp
for cc in ${cases[*]};
do
  echo ${cc}
  docker compose run --rm backend sh -c "python manage.py genomic_db_query_utils --oncokbcna --actionable --cohortcode=${cc}"
  docker compose run --rm backend sh -c "python manage.py genomic_db_query_utils --oncokbsnv --actionable --cohortcode=${cc}"
  docker compose run --rm backend sh -c "python manage.py genomic_db_query_utils --cgiquery --cna --actionable --cohortcode=${cc}"
  docker compose run --rm backend sh -c "python manage.py genomic_db_query_utils --cgiquery --snv --actionable --cohortcode=${cc}"
done
