#!/bin/bash

#SBATCH --job-name=snv_annotation
#SBATCH --output=./logs/%A_%a.txt
#SBATCH --error=./logs/%A_%a.err
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=5G
#SBATCH	--partition=general,evmbig
#SBATCH --exclude=evm06,evm07,evm08,evm09,evm10,evmfull01,evmbig
#SBATCH --array=1-850

echo $1
pid=$(sed -n ${SLURM_ARRAY_TASK_ID}p $1)

echo $pid
source /mnt/storageSmall8/work/aimaaral/oncodash/venv/bin/activate

srun python /mnt/storageSmall8/work/aimaaral/oncodash/wgs_data_adapter.py --somatic_variants /mnt/storageSmall8/work/aimaaral/oncodash/byPatient_CSVs/ --cn_annotations /mnt/storageSmall8/work/aimaaral/oncodash/cnGenesFolder/ --ascatestimates /mnt/storageSmall8/work/aimaaral/oncodash/combinedAscatEstimates.csv --output /mnt/storageSmall8/work/aimaaral/oncodash/snv_annotations/${pid}.csv --pid ${pid} --cores 1 
