import numpy as np
import matplotlib.pyplot as plt
import sys
import pandas as pd
import os
from scipy.stats import pearsonr

# data_file = r'/Users/robert/Downloads/Internship2025/Optstat_simulations/new/opstat_snr_comparison.csv'

# output_dir = r'/Users/robert/Downloads/Internship2025/Optstat_simulations/new/plots'


class create_plots:
    def __init__(self, datadir, comparison):
        self.data_file = os.path.join(datadir, 'opstat_snr_comparison.csv')
        self.output_dir = os.path.join(datadir, 'plots')
        os.makedirs(self.output_dir, exist_ok=True)
        self.data = pd.read_csv(self.data_file)

        self.textdir = os.path.join(datadir, 'dats')
        os.makedirs(self.textdir, exist_ok=True)

        self.comparison = comparison # 'parameter' or 'signature', parameter means comparing SW and no_SW, signature means comparing HD and dipolar

        self.SW_HD = []
        self.no_SW_HD = []
        self.SW_dipolar = []
        self.no_SW_dipolar = []

        self.angles = [0, 3, 6, 9, 12, 15, 20, 25, 30, 45, 60]  # hardcoded for now

    def process_data(self):
        for index, row in self.data.iterrows():
            if "test" not in row['Directory']:
                if 'no_SW' in row['Directory']:
                    self.no_SW_HD.append(row['SNR_HD'])
                    self.no_SW_dipolar.append(row['SNR_dipolar'])
                else:
                    self.SW_HD.append(row['SNR_HD'])
                    self.SW_dipolar.append(row['SNR_dipolar'])
        

    def determine_y_values(self, type):
        if self.comparison == 'parameter':
            if type == 'values':
                return (self.SW_HD, self.no_SW_HD, self.SW_dipolar, self.no_SW_dipolar)
            elif type == 'labels':
                return ('SW HD', 'No SW HD', 'SW Dipolar', 'No SW Dipolar', 'SW vs No SW (HD)', 'SW vs No SW (Dipolar)')
            else:
                raise ValueError("Invalid type specified. Use 'values' or 'labels'.")
        elif self.comparison == 'signature':
            if type == 'values':
                return (self.SW_HD, self.SW_dipolar, self.no_SW_HD, self.no_SW_dipolar)
            elif type == 'labels':
                return ('SW HD', 'SW Dipolar', 'No SW HD', 'No SW Dipolar', 'HD vs Dipolar (SW)', 'HD vs Dipolar (No SW)')
            else:
                raise ValueError("Invalid type specified. Use 'values' or 'labels'.")
        else:
            raise ValueError("Invalid comparison type. Use 'parameter' or 'signature'.")

    def plot(self):
        self.process_data()
        y1, y2, y3, y4 = self.determine_y_values(type='values')
        l1, l2, l3, l4, title1, title2 = self.determine_y_values(type='labels')

        fig, ax1 = plt.subplots()

        ax1.plot(self.angles, y1, 'o-', label=l1, color='green')
        ax1.plot(self.angles, y2, 'o-', label=l2, color='red')

        ax1.set_xlabel('Angle (degrees)')
        ax1.set_ylabel('SNR')
        
        ax1.tick_params(axis='y')

        ax1.legend()
        plt.title(title1)
        plt.grid()
        fig.tight_layout()
        plt.savefig(os.path.join(self.output_dir, f'{title1}.png'), dpi=300, bbox_inches='tight')

        plt.close()

        # Create a new figure for the second plot
        fig, ax1 = plt.subplots()

        ax1.plot(self.angles, y3, 'o-', label=l3, color='orange')
        ax1.plot(self.angles, y4, 'o-', label=l4, color='blue')

        ax1.set_xlabel('Angle (degrees)')
        ax1.set_ylabel('SNR')
        
        ax1.tick_params(axis='y')

        ax1.legend()
        plt.title(title2)
        plt.grid()
        fig.tight_layout()
        plt.savefig(os.path.join(self.output_dir, f'{title2}.png'), dpi=300, bbox_inches='tight')

        plt.close()

        print("Plots saved to:", self.output_dir)

    def calculate_correlation(self):
        self.process_data()
        y1, y2, y3, y4 = self.determine_y_values(type='values')
        l1, l2, l3, l4, title1, title2 = self.determine_y_values(type='labels')

        # For signature comparison (HD vs Dipolar), exclude angle 9 for SW dataset
        if self.comparison == 'signature':
            # Find index of angle 9 (which is at index 3 in the angles list)
            exclude_index = 3  # angle 9 is at index 3 in self.angles
            print(f'')
            
            # Remove the data point at angle 9 for SW HD vs SW Dipolar correlation
            y1_filtered = [val for i, val in enumerate(y1) if i != exclude_index]
            y2_filtered = [val for i, val in enumerate(y2) if i != exclude_index]
            
            val1 = pearsonr(y1_filtered, y2_filtered)
            val2 = pearsonr(y3, y4)  # No SW correlation remains unchanged
        else:
            val1 = pearsonr(y1, y2)
            val2 = pearsonr(y3, y4)
        
        print(f"Pearson r ({l1} vs {l2}) = {val1[0]:.3f}, p = {val1[1]:.3g}")
        print(f"Pearson r ({l3} vs {l4}) = {val2[0]:.3f}, p = {val2[1]:.3g}")

        with open(os.path.join(self.textdir, f'correlation_{self.comparison}.txt'), 'w') as f:
            f.write(f"Pearson r ({l1} vs {l2}) = {val1[0]:.3f}, p = {val1[1]:.3g}\n")
            f.write(f"Pearson r ({l3} vs {l4}) = {val2[0]:.3f}, p = {val2[1]:.3g}\n")
            if self.comparison == 'signature':
                f.write(f"Note: SW HD vs SW Dipolar correlation excludes angle 9 degrees\n")

        print(f"Correlation results saved to: {self.textdir}")


set1 = create_plots(
    #datadir = r'/Users/robert/Downloads/Internship2025/Optstat_simulations/with_30/',
    datadir = r'/Users/robert/Downloads/Internship2025/Optstat_v4',
    comparison='parameter'
)

set1.plot()
set1.calculate_correlation()

set2 = create_plots(
    #datadir = r'/Users/robert/Downloads/Internship2025/Optstat_simulations/with_30/',
    datadir = r'/Users/robert/Downloads/Internship2025/Optstat_v4',
    comparison='signature'
)

set2.plot()
set2.calculate_correlation()


# data_file = r'/Users/robert/Downloads/Internship2025/Optstat_v4/opstat_snr_comparison.csv'

# output_dir = r'/Users/robert/Downloads/Internship2025/Optstat_v4/plots'
# os.makedirs(output_dir, exist_ok=True)

# data = pd.read_csv(data_file)

# SW_HD = []
# no_SW_HD = []
# SW_dipolar = []
# no_SW_dipolar = []

# angles = [0,3,6,9,12,15,20,25,30,45,60] # hardcoded for now

# for index, row in data.iterrows():
#     if "test" not in row['Directory']:
#         if 'no_SW' in row['Directory']:
#             no_SW_HD.append(row['SNR_HD'])
#             no_SW_dipolar.append(row['SNR_dipolar'])
#         else:
#             SW_HD.append(row['SNR_HD'])
#             SW_dipolar.append(row['SNR_dipolar'])

# fig, ax1 = plt.subplots()


# ax1.plot(angles, SW_HD, 'o-', label='SW HD', color='blue')
# ax1.plot(angles, no_SW_HD, 'o-', label='No SW HD', color='orange')

# ax1.set_xlabel('Angle (degrees)')
# ax1.set_ylabel('SNR HD', color='blue')

# ax1.tick_params(axis='y')

# ax1.legend()
# fig.tight_layout()
# plt.title('SNR HD Comparison')
# plt.grid()
# plt.savefig(os.path.join(output_dir, 'snr_hd_comparison.png'), dpi=300)

# plt.close()

# fig, ax1 = plt.subplots()

# ax1.plot(angles, SW_dipolar, 'o-', label='SW Dipolar', color='green')
# ax1.plot(angles, no_SW_dipolar, 'o-', label='No SW Dipolar', color='red')

# ax1.set_xlabel('Angle (degrees)')
# ax1.set_ylabel('SNR Dipolar', color='green')

# ax1.tick_params(axis='y')

# ax1.legend()
# fig.tight_layout()
# plt.title('SNR Dipolar Comparison')
# plt.grid()
# plt.savefig(os.path.join(output_dir, 'snr_dipolar_comparison.png'), dpi=300)

# plt.close()

# print("Plots saved to:", output_dir)

# r_SW, p_value_SW = pearsonr(SW_HD, SW_dipolar)
# r_no_SW, p_value_no_SW = pearsonr(no_SW_HD, no_SW_dipolar)
# print(f"Pearson r (SW) = {r_SW:.3f}, p = {p_value_SW:.3g}")
# print(f"Pearson r (no SW) = {r_no_SW:.3f}, p = {p_value_no_SW:.3g}")