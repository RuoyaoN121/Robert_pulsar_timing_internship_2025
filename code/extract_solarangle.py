import os
import subprocess
import pandas as pd
import sys

def process_pulsars(directory, output_csv):
    data = []
    
    for filename in os.listdir(directory):
        if filename.endswith(".par"):  # Check for .par files
            pulsar_name = filename[:-4]  # Remove extension to get name
            if not pulsar_name[-1].isdigit():
                pulsar_name = filename.split('_')[0]
                name_part = filename.split('.')[0]
            print(f"Processing {pulsar_name}")

            if name_part is not None:
                tim_file = os.path.join(directory, name_part + ".tim")
            else:
                tim_file = os.path.join(directory, pulsar_name + ".tim")
            par_file = os.path.join(directory, filename)
            
            if not os.path.exists(tim_file):
                print(f"Skipping {pulsar_name}, missing .tim file")
                continue
            
            # Run tempo2 command
            command = ["tempo2", "-f", par_file, tim_file, "-output", "general2", "-s", "{sat} {solarangle}\n"]
            result = subprocess.run(command, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Error processing {pulsar_name}: {result.stderr}")
                continue
            
            # Parse output
            for line in result.stdout.strip().split("\n"):
                parts = line.split()
                if len(parts) == 2:
                    mjd, solar_psr_angle = parts
                    data.append([pulsar_name, float(mjd), float(solar_psr_angle)])
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(data, columns=["Pulsar", "MJD", "SolarPSRAngle"])
    output_csv = os.path.join(directory, 'obsinfo', output_csv)
    df.to_csv(output_csv, index=False)
    print(f"CSV saved to {output_csv}")

# Example usage
if len(sys.argv) < 2:
    print("Usage: python script.py <directory>")
    sys.exit(1)

directory = sys.argv[1]
basedir = os.getcwd()
directory = os.path.join(basedir, directory)

output_csv = "pulsar_solar_angles.csv"
process_pulsars(directory, output_csv)
