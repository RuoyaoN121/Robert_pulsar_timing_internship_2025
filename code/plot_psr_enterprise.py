from enterprise.pulsar import Pulsar
import matplotlib.pyplot as plt
import sys
import glob
import os
import matplotlib
import pickle

matplotlib.use('Agg')

# Get data directory from command-line argument
datadir = str(sys.argv[1])
dirname = datadir.split('/')[1]


pklpath = os.path.join('/fred/oz002/users/mbailes/astral/timing2025/pkls', f"{dirname}.pkl")

##### Read the enterprise pickle file 
with open(pklpath,'rb') as fp:
    psr = pickle.load(fp)

psrnames = list(psr.keys())
print(f"Found {len(psrnames)} pulsars in the pickle file.")
psrs = [psr[p] for p in psrnames]

output_dir = f"../Optstat_v3/pngs/{dirname}/"
os.makedirs(output_dir, exist_ok=True)

'''
# Find par and tim files
parfile = sorted(glob.glob(datadir + 'J*.par'))
timfile = sorted(glob.glob(datadir + 'J*.tim'))

# Ensure output directory exists
output_dir = f"../Optstat_v3/pngs/{dirname}/"
os.makedirs(output_dir, exist_ok=True)

# Load pulsar data
psrs = []
ephemeris = 'DE440'

print("Loading pulsars...")
for p, t in zip(parfile, timfile):
    try:
        pulsar = Pulsar(p, t, ephem=ephemeris)
        psrs.append(pulsar)
        print(f"Loaded {pulsar.name}")
    except Exception as e:
        print(f"Error loading {p}: {e}")
        continue
'''



# Plot for each pulsar
print("Plotting pulsars...")
for pulsar in psrs:
    try:
        toas_mjd = pulsar.toas / 86400.0
        residuals = pulsar.residuals
        errors = pulsar.toaerrs

        plt.figure(figsize=(10, 6))
        plt.errorbar(toas_mjd, residuals, yerr=errors, fmt='x', color='blue', label=pulsar.name)
        plt.xlabel("MJD")
        plt.ylabel("Residual (s)")
        plt.title(f"TOA Residuals vs. MJD for {pulsar.name}")
        plt.grid(True)
        plt.legend()

        filename = f"{output_dir}/{pulsar.name}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved {pulsar.name}.png")
    except Exception as e:
        print(f"Error plotting {pulsar.name}: {e}")
        plt.close()  # Ensure figure is closed on error
        continue