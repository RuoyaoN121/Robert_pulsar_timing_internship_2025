import os
import sys
import re
from decimal import Decimal
from collections import defaultdict

def process_tim_file(file_path):
    """
    Process a .tim file:
    1. Remove all lines containing 'FORMAT 1'
    2. Add one 'FORMAT 1' line and ensure only one 'MODE 1' line exists
    3. Sort the remaining lines by the value in the third column
    4. Remove lines with duplicate MJD values
    """
    try:
        # Read the file
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        # Extract pulsar name from filename
        pulsar_name = os.path.basename(file_path).split('.')[0]
        
        # Filter out lines containing FORMAT 1
        filtered_lines = [line for line in lines if 'FORMAT 1' not in line]
        
        # Parse data lines for sorting
        data_lines = []
        other_lines = []
        has_mode_1 = False
        
        for line in filtered_lines:
            # Skip empty lines
            if line.strip() == '':
                continue
            
            # Check if line contains MODE 1
            if line.strip() == 'MODE 1':
                has_mode_1 = True
                continue
                
            # Check if this is a data line by trying to split it
            parts = line.strip().split()
            if len(parts) >= 3:
                try:
                    # Try to convert the third column to Decimal for sorting
                    timestamp = Decimal(parts[2])
                    data_lines.append((timestamp, line))
                except:
                    # If conversion fails, it's not a data line
                    other_lines.append(line)
            else:
                # Not a data line
                other_lines.append(line)
        
        # Sort data lines by timestamp
        data_lines.sort(key=lambda x: x[0])
        
        # Remove duplicate MJD entries
        unique_data_lines = []
        seen_mjds = set()
        redundant_count = 0
        
        for mjd, line in data_lines:
            if mjd in seen_mjds:
                redundant_count += 1
                continue
            seen_mjds.add(mjd)
            unique_data_lines.append(line)
        
        # Create the modified file content
        # Start with FORMAT 1 and MODE 1 (if needed)
        modified_content = ["FORMAT 1\n"]
        if not has_mode_1:
            modified_content.append("MODE 1\n")
        
        # Add other non-data lines
        modified_content.extend(other_lines)
        
        # Add sorted and deduplicated data lines
        modified_content.extend(unique_data_lines)
        
        # Write back to the file
        with open(file_path, 'w') as file:
            file.writelines(modified_content)
        
        return True, pulsar_name, redundant_count
    
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return False, None, 0

def process_directory(directory_path):
    """
    Process all .tim files in the specified directory
    """
    if not os.path.isdir(directory_path):
        print(f"Error: {directory_path} is not a valid directory")
        return
    
    # Find all .tim files
    tim_files = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.tim'):
                tim_files.append(os.path.join(root, file))
    
    if not tim_files:
        print(f"No .tim files found in {directory_path}")
        return
    
    print(f"Found {len(tim_files)} .tim files to process")
    
    # Process each file
    success_count = 0
    redundant_by_pulsar = defaultdict(int)
    total_redundant = 0
    
    for file_path in tim_files:
        success, pulsar_name, redundant_count = process_tim_file(file_path)
        if success:
            success_count += 1
            redundant_by_pulsar[pulsar_name] += redundant_count
            total_redundant += redundant_count
            print(f"Successfully processed {file_path} - removed {redundant_count} redundant lines")
    
    print(f"\nSuccessfully processed {success_count} out of {len(tim_files)} files")
    print(f"Total redundant lines removed: {total_redundant}")
    print("\nRedundant lines removed by pulsar:")
    for pulsar, count in sorted(redundant_by_pulsar.items()):
        if count > 0:
            print(f"  {pulsar}: {count} redundant lines removed")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python sort_tim.py <directory_path>")
    else:
        directory_path = sys.argv[1]
        if not os.path.isabs(directory_path):
            directory_path = os.path.join(os.getcwd(), directory_path)
        process_directory(directory_path)
