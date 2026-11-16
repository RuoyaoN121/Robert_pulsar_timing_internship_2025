import numpy as np
import os
import json
import matplotlib.pyplot as plt
from enterprise.pulsar import Pulsar
from enterprise.signals import signal_base
from enterprise_extensions.frequentist import optimal_statistic as opt_stat
from scipy.stats import norm
import sys
import glob

# Load pulsars and PTA
datadir = str(sys.argv[1])
parfiles = sorted(glob.glob(datadir + 'J*.par'))
timfiles = sorted(glob.glob(datadir + 'J*.tim'))
psrs = [Pulsar(p, t, ephem='DE440') for p, t in zip(parfiles, timfiles)]
with open('pta_fixed_gamma.pkl', 'rb') as f:  # Adjust as needed
    import dill
    pta = dill.load(f)

# Load chains and find MAP
outdir = sys.argv[2]
chain = np.loadtxt(os.path.join(outdir, 'chain_1.txt'))
ndim = len(pta.param_names)
lnprob = chain[:, ndim]
map_idx = np.argmax(lnprob)
map_params = dict(zip(pta.param_names, chain[map_idx, :ndim]))

# Optimal Statistic
ostat_hd = opt_stat.OptimalStatistic(psrs, pta=pta, orf='hd')
ostat_dip = opt_stat.OptimalStatistic(psrs, pta=pta, orf='dipole')
ostat_mono = opt_stat.OptimalStatistic(psrs, pta=pta, orf='monopole')

xi, rho, sig, OS_hd, OS_sig_hd = ostat_hd.compute_os(params=map_params)
_, _, _, OS_dip, OS_sig_dip = ostat_dip.compute_os(params=map_params)
_, _, _, OS_mono, OS_sig_mono = ostat_mono.compute_os(params=map_params)

# Binning for HD plot
def weightedavg(rho, sig):
    weights, avg = 0., 0.
    for r, s in zip(rho, sig):
        weights += 1./(s*s)
        avg += r/(s*s)
    return avg/weights, np.sqrt(1./weights)

npairs = 216  # For 81 pulsars
idx = np.argsort(xi)
xi_sorted, rho_sorted, sig_sorted = xi[idx], rho[idx], sig[idx]
xi_mean, xi_err, rho_avg, sig_avg = [], [], [], []
i = 0
while i < len(xi_sorted):
    xi_mean.append(np.mean(xi_sorted[i:i+npairs]))
    xi_err.append(np.std(xi_sorted[i:i+npairs]))
    r, s = weightedavg(rho_sorted[i:i+npairs], sig_sorted[i:i+npairs])
    rho_avg.append(r)
    sig_avg.append(s)
    i += npairs

# Convert lists to NumPy arrays
xi_mean = np.array(xi_mean)
xi_err = np.array(xi_err)
rho_avg = np.array(rho_avg)
sig_avg = np.array(sig_avg)

# HD curve
def get_HD_curve(zeta):
    coszeta = np.cos(zeta * np.pi / 180.)
    HD = 3. * (1./3. + (1.-coszeta)/2. * (np.log((1.-coszeta)/2.) - 1./6.))
    return HD / 2.

zeta = np.linspace(0.01, 180, 100)
HD = get_HD_curve(zeta)

# Plot
plt.figure(figsize=(12, 7))
plt.errorbar(xi_mean * 180/np.pi, rho_avg, xerr=xi_err * 180/np.pi, yerr=sig_avg, 
             marker='o', ls='', color='#003f5c', capsize=7.5, label='Correlations')
plt.plot(zeta, OS_hd * HD, ls='--', color='#117733', lw=3, label='Hellings-Downs')
plt.xlabel(r'$\zeta$ ($^{\circ}$)', fontsize=15)
plt.ylabel(r'$\hat{A}^2 \Gamma(\zeta_{ab})$', fontsize=15)
plt.legend(fontsize=15)
plt.savefig(os.path.join(outdir, 'HD_curve.png'), dpi=100)
plt.close()

# Per-pulsar stats
npsr = len(psrs)
gof = np.zeros(npsr)
rho_expected = OS_hd * get_HD_curve(xi)
f = open(os.path.join(outdir, 'crosscorr.dat'), 'w')
i = 0
for ii in range(npsr-1):
    for jj in range(ii+1, npsr):
        gof[ii] += ((rho[i] - rho_expected[i]) / sig[i])**2
        gof[jj] += ((rho[i] - rho_expected[i]) / sig[i])**2
        f.write(f"{psrs[ii].name} {psrs[jj].name} {rho[i]/sig[i]} {rho[i]} {sig[i]} {xi[i]}\n")
        i += 1
f.close()

# Save stats
with open(os.path.join(outdir, 'SNR.dat'), 'w') as f:
    f.write(f"HD: {OS_hd} {OS_sig_hd} {OS_hd/OS_sig_hd}\n")
    f.write(f"Dipole: {OS_dip} {OS_sig_dip} {OS_dip/OS_sig_dip}\n")
    f.write(f"Monopole: {OS_mono} {OS_sig_mono} {OS_mono/OS_sig_mono}\n")