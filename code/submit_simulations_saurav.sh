#!/bin/bash

BASE_NAME=${1}
NUM_RUNS=${2}

echo "Submitting $NUM_RUNS jobs with base name: $BASE_NAME"

for i in $(seq 1 $NUM_RUNS); do
    JOB_NAME="${BASE_NAME}_${i}"
    echo "Submitting job $i: $JOB_NAME"
    
    sbatch --job-name="$JOB_NAME" \
           /fred/oz002/users/mbailes/astral/timing2025/bin/submit_saurav_crn.sh $i $BASE_NAME
    
    # Small delay to avoid overwhelming the scheduler
    sleep 1
done

echo "All $NUM_RUNS jobs submitted successfully!"
echo "Monitor jobs with: squeue -u \$USER"