#!/bin/bash

rm ./logs/*
sbatch --array=1-$(cat ${1} | wc -l) ./snv_annotation.sbatch $1
