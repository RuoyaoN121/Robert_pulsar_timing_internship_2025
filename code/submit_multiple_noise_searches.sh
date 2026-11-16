#!/bin/bash

# Script to submit multiple noise search jobs with different arguments (1-10)
SUBMIT_SCRIPT="/fred/oz002/users/mbailes/astral/timing2025/bin/submit_noise_search.sh"

echo "Submitting 10 noise search jobs..."

for i in {51..60}
do
    # Submit the job with the argument i
    JOB_ID=$(sbatch $SUBMIT_SCRIPT $i | awk '{print $4}')
    
    echo "Submitted job for argument $i with Job ID: $JOB_ID"
done

echo "All jobs submitted!"
