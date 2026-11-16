#!/bin/bash
#SBATCH --job-name=GWB_free_gamma
#SBATCH --output=/fred/oz002/users/mbailes/astral/timing2025/Optstat/Bayesian_GWB_DM_RN_free_gamma_GWB_search_2_advanced_cuts/GWB_free_gamma_%j.out
#SBATCH --error=/fred/oz002/users/mbailes/astral/timing2025/Optstat/Bayesian_GWB_DM_RN_free_gamma_GWB_search_2_advanced_cuts/GWB_free_gamma_%j.err
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=32
#SBATCH --mem=128G
#SBATCH --mail-type=ALL
#SBATCH --mail-user=ruoyaoni121@gmail.com

module load apptainer
apptainer exec -B /fred/oz002/users/mbailes/astral/timing2025/GWB_search_2_advanced_cuts/:/fred/oz002/users/mbailes/astral/timing2025/GWB_search_2_advanced_cuts/ -B /fred/oz002/users/mbailes/astral/timing2025/Optstat:/fred/oz002/users/mbailes/astral/timing2025/Optstat -B /fred/oz002/users/mbailes/astral/timing2025/bin:/fred/oz002/users/mbailes/astral/timing2025/bin -B /fred/oz002/users/mbailes/astral/timing2025/jsons:/fred/oz002/users/mbailes/astral/timing2025/jsons /home/rni/my_container.sif python /fred/oz002/users/mbailes/astral/timing2025/bin/sample_free_spectral_index.py /fred/oz002/users/mbailes/astral/timing2025/GWB_search_2_advanced_cuts/
