#!/bin/bash

rm ./logs/*
sbatch --array=1-$(cat ${1} | wc -l) ./cna_annotation.sbatch $1
