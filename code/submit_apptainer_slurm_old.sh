#!/bin/bash
#SBATCH --job-name=pulsar_analysis
#SBATCH --output=pulsar_analysis_%j.out  # Log file
#SBATCH --error=pulsar_analysis_%j.err   # Error log file
#SBATCH --time=0:20:00  # Adjust time as needed (HH:MM:SS)
#SBATCH --mem=16G        # Adjust memory as needed
#SBATCH --cpus-per-task=4  # Adjust CPU count as needed
#SBATCH --ntasks=1

# Load Apptainer module
ml apptainer

# Set container path
CONTAINER="my_container.sif"

# Set working directory (modify if needed)
WORKDIR="/fred/oz002/users/mbailes/astral/timing2025/bin"

# Set data directory (passed as an argument)
DATA_DIR="$1"

# Check if directory argument is provided
if [ -z "$DATA_DIR" ]; then
    echo "Usage: sbatch submit_pulsar_analysis.sh <directory>"
    exit 1
fi

# Run the Python script inside the Apptainer container
apptainer exec -B /fred,$HOME "$CONTAINER" python "$WORKDIR/plot_psr_enterprise.py" "$DATA_DIR"

echo "SLURM job completed."
