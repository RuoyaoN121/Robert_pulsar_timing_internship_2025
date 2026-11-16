#!/bin/bash
#SBATCH --cpus-per-task=1
#SBATCH --ntasks=1
#SBATCH --time=120:00:00
#SBATCH --mem=8GB

#SBATCH -o /fred/oz002/users/mbailes/astral/timing2025/pta_analysis_simulations/job_outfiles/%x_%j.out


ml gcc/12.2.0 openmpi/4.1.4

ml apptainer

# Accept run number as parameter
RUN_NUMBER=${1}
BASE_RESULT_DIR=${2}

i=0
while [ $i -lt 1 ]; do
    apptainer run -B /fred,$HOME /fred/oz002/users/mbailes/astral/timing2025/bin/apptainer_220525.sif python /fred/oz002/users/mbailes/astral/timing2025/bin/robert/saurav_simulation_crn.py ${RUN_NUMBER} ${BASE_RESULT_DIR}

    if [[ "$?" -eq 139 ]]; then
        echo "segfault !";
    else echo "no segfault !";
        ((i++));
    fi;
done

echo done