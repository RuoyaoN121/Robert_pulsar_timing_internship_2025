import os
import subprocess
import sys

# Configuration
datadir = r'/fred/oz002/users/mbailes/astral/timing2025/GWB_search_2_advanced_cuts/'
base_dir = r'/fred/oz002/users/mbailes/astral/timing2025/Optstat'
scripts_dir = '/fred/oz002/users/mbailes/astral/timing2025/bin'  # Where your Python files are
apptainer_image = f"{os.environ['HOME']}/my_container.sif"  # Adjust if .sif is elsewhere
email = 'ruoyaoni121@gmail.com'  # For SLURM notifications

# Bind paths for Apptainer
bind_paths = f"-B {datadir}:{datadir} -B {base_dir}:{base_dir} -B {scripts_dir}:{scripts_dir} -B /fred/oz002/users/mbailes/astral/timing2025/jsons:/fred/oz002/users/mbailes/astral/timing2025/jsons"
slurm_template = """#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --output={outdir}/{job_name}_%j.out
#SBATCH --error={outdir}/{job_name}_%j.err
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=32
#SBATCH --mem=128G
#SBATCH --mail-type=ALL
#SBATCH --mail-user={email}

module load apptainer
apptainer exec {bind_paths} {apptainer_image} python {scripts_dir}/{script} {datadir}
"""

# Job configurations
jobs = [
#    {
#        'job_name': 'GWB_fixed_gamma',
#        'script': 'sample_fixed_spectral_index.py',
#        'outdir': os.path.join(base_dir, 'Bayesian_GWB_DM_RN_fixed_gamma_' + datadir.split('/')[-2])
#    },
    {
        'job_name': 'GWB_free_gamma',
        'script': 'sample_free_spectral_index.py',
        'outdir': os.path.join(base_dir, 'Bayesian_GWB_DM_RN_free_gamma_' + datadir.split('/')[-2])
    }
]

# Generate and submit SLURM scripts
for job in jobs:
    slurm_script = slurm_template.format(
        job_name=job['job_name'],
        outdir=job['outdir'],
        email=email,
        bind_paths=bind_paths,
        apptainer_image=apptainer_image,
        scripts_dir=scripts_dir,
        script=job['script'],
        datadir=datadir
    )
    slurm_file = f"{job['job_name']}.slurm"
    with open(slurm_file, 'w') as f:
        f.write(slurm_script)
    
    # Submit job
    result = subprocess.run(['sbatch', slurm_file], capture_output=True, text=True)
    print(f"Submitted {job['job_name']}: {result.stdout.strip()}")

# Post-processing submission
for job in jobs:
    post_slurm = slurm_template.format(
        job_name=f"{job['job_name']}_post",
        outdir=job['outdir'],
        email=email,
        bind_paths=bind_paths,
        apptainer_image=apptainer_image,
        scripts_dir=scripts_dir,
        script='post_process.py',
        datadir=f"{datadir} {job['outdir']}"
    )
    post_file = f"{job['job_name']}_post.slurm"
    with open(post_file, 'w') as f:
        f.write(post_slurm)
    print(f"Generated {post_file}. Run 'sbatch {post_file}' after sampling completes.")