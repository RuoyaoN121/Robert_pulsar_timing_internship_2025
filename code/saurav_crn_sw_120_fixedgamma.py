# usr/bin/env python
# coding: utf-8

import os
import sys
import numpy as np
import json
import pickle
from enterprise import constants as const
from enterprise.pulsar import Pulsar
from enterprise.signals import signal_base
from enterprise.signals import white_signals
from enterprise.signals import gp_signals
from enterprise.signals import parameter
from enterprise.signals import selections
from enterprise.signals import utils
from enterprise.signals import gp_priors
from enterprise.signals import deterministic_signals
from enterprise.signals import gp_bases
from enterprise_extensions.blocks import common_red_noise_block
# from enterprise_extensions import hypermodel
from enterprise_extensions import hypermodel  ## This is just to test the new jump proposal from Matt.
#from PTMCMCSampler.PTMCMCSampler import PTSampler as ptmcmc

#import bilby
#sys.path.insert(0, '/fred/oz002/users/akulkarn/softwares/enterprise_warp/')
#from enterprise_warp import bilby_warp

from enterprise_extensions.chromatic.solar_wind import *
from enterprise_extensions.chromatic.chromatic import chrom_yearly_sinusoid

def get_pulsar_noise_params(psr):
    """Retrun the list of noise parameters with their values for a particular pulsar
    """
    p_dict = {}
    for params in Noise_MPTA:
        if psr in params:
            p_dict[params] = Noise_MPTA[params]
    return p_dict

def dm_noise(log10_A,gamma,Tspan,components=120,option="powerlaw"):
    """
    A term to account for stochastic variations in DM. It is based on spin
    noise model, with Fourier amplitudes depending on radio frequency nu
    as ~ 1/nu^2.
    """
    nfreqs = 120
    if option=="powerlaw":
      #pl = utils.powerlaw(log10_A=log10_A, gamma=gamma, components=components)
      pl = utils.powerlaw(log10_A=log10_A, gamma=gamma)
      #pl = enterprise.signals.gp_priors.powerlaw_no_components(log10_A=log10_A, gamma=gamma)

    #elif option=="turnover":
    #  fc = parameter.Uniform(self.params.sn_fc[0],self.params.sn_fc[1])
    #  pl = powerlaw_bpl(log10_A=log10_A, gamma=gamma, fc=fc,
    #                    components=components)
    dm_basis = utils.createfourierdesignmatrix_dm(nmodes = components,
                                                  Tspan=Tspan)
    dmn = gp_signals.BasisGP(pl, dm_basis, name='dm_gp')

    return dmn

@signal_base.function
def chrom_gaussian_bump(toas,freqs, log10_Amp,sign_param,t0,sigma,idx):
    """Function to define chromatic bump signal"""
    wf = 10**log10_Amp * np.exp(-(toas - t0)**2/2/sigma**2)
    return np.sign(sign_param) * wf * (1400 / freqs) ** idx

chainnum = sys.argv[1]


#num = sys.argv[2]

#med_map = sys.argv[3]

"""if 'efac' in chainnum:
    onlyefac = True
else:
    onlyefac = False"""

#grp = int(sys.argv[3])

"""gw_mod = "/".join(chainnum.split("/")[0:-2])
if 'WN_RN_DM' in chainnum:
    inj_mod = 'WN_RN_DM'
if 'real_inj' in chainnum:
    inj_mod = 'real_inj'
    if 'swPrior' in chainnum:
        inj_mod = 'real_inj_swPrior'
    if 'rmvStocSW' in chainnum:
        inj_mod = 'real_inj_rmvStocSW'"""


######## Get all the pulsar objects ###########
#with open("/fred/oz002/users/smishra/work/PhD/RM_pat_studies/RM_measurement/enterprise/crn/pulsar_matt.txt") as fp:
#    psrnames = fp.read().splitlines()


#### Read in the list of pulsars to be removed from the json file #####
#with open(os.path.join("/fred/oz002/users/smishra/work/PhD/RM_pat_studies/RM_measurement/enterprise/crn/",gw_mod,"remove_psr.json")) as fp:
#    remove_psr = json.load(fp)
# remove_psr = ["J1455-3330",    ######## tempo2 post-fit residuals have wider scatter than pre-fit residuals
#               ]

"""with open("/fred/oz002/users/smishra/work/PhD/RM_pat_studies/RM_measurement/enterprise/crn/remove.txt") as fp:
   remove_psr = fp.read().splitlines()

for r in remove_psr:
    psrnames.remove(r)"""

"""psr = {}
for p in psrnames:
    pfile = os.path.join("/fred/oz002/users/smishra/work/PhD/RM_pat_studies/RM_measurement/enterprise/crn/pp_8/",p+".par") 
    tfile = os.path.join("/fred/oz002/users/smishra/work/PhD/RM_pat_studies/RM_measurement/enterprise/crn/pp_8/",p+".tim")
    psr[p] = Pulsar(pfile, tfile, ephem='DE440')

with open("/fred/oz002/users/smishra/work/PhD/RM_pat_studies/RM_measurement/enterprise/crn/psr_objects.pkl", 'wb') as fp:
    pickle.dump(psr, fp)

print("Pulsar objects have been saved to psr_objects.pkl")


exit()"""

dirname = 'GWB_search_3'
pklpath = os.path.join('/fred/oz002/users/mbailes/astral/timing2025/pkls', f"{dirname}.pkl")


##### Read the enterprise pickle file 
with open(pklpath,'rb') as fp:
    psr = pickle.load(fp)

psrnames = list(psr.keys())

selection = selections.Selection(selections.by_backend)

######## Define prior on various Noise processes #########
"""efac = parameter.Uniform(0.01, 4)
equad = parameter.Uniform(-10, -5)
ecorr = parameter.Uniform(-10, -5)"""

efac = parameter.Constant()
equad = parameter.Constant()
ecorr = parameter.Constant()

log10_A_dm = parameter.Uniform(-20, -11)
gamma_dm = parameter.Uniform(0, 10)

log10_A_rn = parameter.Uniform(-20, -11)
gamma_rn = parameter.Uniform(0, 10)

log10_A_chrom_prior = parameter.Uniform(-20, -11)
gamma_chrom_prior = parameter.Uniform(0, 10)
idx = parameter.Uniform(0, 12)

"""n_earth = parameter.Uniform(0, 20)('common_n_earth')
#log10_A_sw = parameter.Uniform(-10, 1)
log10_A_sw = parameter.Uniform(-10, -2)('common_log10_A_sw')
gamma_sw = parameter.Uniform(-5, 5)('common_gamma_sw')
sw_components = 120
log10_rho_sw = parameter.Uniform(-6, 2, size=sw_components)('common_log10_rho_gp_sw')"""

n_earth = parameter.Uniform(0, 20)
#log10_A_sw = parameter.Uniform(-10, 1)
log10_A_sw = parameter.Uniform(-10, -2)
gamma_sw = parameter.Uniform(-5, 5)
sw_components = 120
log10_rho_sw = parameter.Uniform(-6, 2, size=sw_components)
###################################
""" Include chromatic annual variations"""
log10_A_chrom1yr_prior = parameter.Uniform(-10, -4)
phase_chrom1yr_prior = parameter.Uniform(0, 2*np.pi)
idx_chrom1yr_prior = parameter.Uniform(0, 12)

deter_chrom1yr = chrom_yearly_sinusoid(log10_Amp=log10_A_chrom1yr_prior,phase=phase_chrom1yr_prior,idx=idx_chrom1yr_prior)
chrom1yr = deterministic_signals.Deterministic(deter_chrom1yr, name='chrom1yr')


"""Include chromatic bump """
idx_chrom_bump_prior = parameter.Uniform(0, 12)
log10_A_chrom_bump_prior = parameter.Uniform(-10, -4)
sigma_chrom_bump_prior = parameter.Uniform(0, 126144000)
sign_chrom_bump_prior = parameter.Uniform(-1, 1)
t0_chrom_bump_prior = parameter.Uniform(4924800000, 5227632000)

deter_chrombump = chrom_gaussian_bump(log10_Amp=log10_A_chrom_bump_prior,sign_param=sign_chrom_bump_prior,t0=t0_chrom_bump_prior,sigma=sigma_chrom_bump_prior,idx=idx_chrom_bump_prior)
chrom_bump = deterministic_signals.Deterministic(deter_chrombump, name='chrom_bump')


"""
Define common red noise
"""
# Powerlaw no correlations
crn = common_red_noise_block(psd='powerlaw', prior='log-uniform', components=120, logmin=-16, logmax=-11, orf=None, name='gw', gamma_val=13./3.)

# # Broken powerlaw no correlations
# crn = common_red_noise_block(psd='broken_powerlaw', prior='log-uniform',
#                              components=30, orf=None, name='common')
# # Powerlaw Hellings-Downs
# crn = common_red_noise_block(psd='powerlaw', prior='log-uniform',
#                              components=30, orf='hd', name='gwb')
# # Powerlaw Monopole
# crn = common_red_noise_block(psd='powerlaw', prior='log-uniform',
#                              components=30, orf='monopole', name='monopole')
# # Powerlaw Dipole
# crn = common_red_noise_block(psd='powerlaw', prior='log-uniform',
#                              components=30, orf='dipole', name='dipole')


########## Define timing model ###############

tm = gp_signals.TimingModel(use_svd=True)

# ######################################################################################################################
### global solar wind signal
deter_sw = solar_wind(n_earth=n_earth)
mean_sw = deterministic_signals.Deterministic(deter_sw, name='n_earth')

max_psr, min_psr=np.zeros(len(psrnames)), np.zeros(len(psrnames))
for i,p in enumerate(psrnames):
    max_psr[i] = psr[p].toas.max()
    min_psr[i] = psr[p].toas.min()
Tspan_sw = np.max(max_psr) - np.min(min_psr)
print(Tspan_sw)
print("Tspan is ",Tspan_sw/np.float128(365.25*86400))

#Tspan = psr[p].toas.max() - psr[p].toas.min()
sw_components = 120  
Free_spectrum = False ## False means power law spectrum
#### power law spectrum
if Free_spectrum:
    sw_spectrum = gp_priors.free_spectrum(log10_rho=log10_rho_sw)
    sw_basis = createfourierdesignmatrix_solar_dm(nmodes=sw_components, Tspan=Tspan_sw)
    sw = gp_signals.BasisGP(sw_spectrum, sw_basis, name='sw_specturm')
else:
    sw_prior = utils.powerlaw(log10_A=log10_A_sw, gamma=gamma_sw)
    sw_basis = createfourierdesignmatrix_solar_dm(nmodes=sw_components, Tspan=Tspan_sw)
    sw = gp_signals.BasisGP(sw_prior, sw_basis, name='gp_sw')

####free spectrum
#sw_spectrum = gp_priors.free_spectrum(log10_rho=log10_rho_sw)
#sw_basis = createfourierdesignmatrix_solar_dm(nmodes=sw_components, Tspan=Tspan_sw)
#sw = gp_signals.BasisGP(sw_spectrum, sw_basis, name='sw_specturm')

# ######################################################################################################################
# with open("/fred/oz002/users/akulkarn/MPTA_17April24/dataset/noise/heirarch_values.json",'r') as fp:
#     Noise_MPTA = json.load(fp)
"""with open('/fred/oz002/users/smishra/work/PhD/RM_pat_studies/RM_measurement/enterprise/simulations/postCoC/saurav_realistic_PTA/new_app/heirarch_values_without_J0955.json','r') as fp:
    Noise_MPTA = json.load(fp)"""

with open('/fred/oz005/users/smishra/work/enterprise/new_app/noise_median_updated.json','r') as fp:
    Noise_MPTA = json.load(fp)

s_all = {}

for p in psrnames:
    p_dict = get_pulsar_noise_params(p)
    
    ef = white_signals.MeasurementNoise(efac=efac, selection=selection)
    s_all[p] = ef + tm + crn 

    sw_prior = utils.powerlaw(log10_A=log10_A_sw, gamma=gamma_sw)
    sw_basis = createfourierdesignmatrix_solar_dm(nmodes=sw_components, Tspan=Tspan_sw)
    sw = gp_signals.BasisGP(sw_prior, sw_basis, name='gp_sw')
    s_all[p] += sw

    deter_sw = solar_wind(n_earth=n_earth)
    mean_sw = deterministic_signals.Deterministic(deter_sw, name='n_earth')
    s_all[p] += mean_sw


    
    if any(['equad' in x for x in p_dict.keys()]):
        eq = white_signals.TNEquadNoise(log10_tnequad=equad,selection=selection)
        s_all[p] += eq
    if any(['ecorr' in x for x in p_dict.keys()]):
        #ec = gp_signals.EcorrBasisModel(log10_ecorr=ecorr,selection=selection)
        ec = white_signals.EcorrKernelNoise(log10_ecorr=ecorr,selection=selection)
        s_all[p] +=  ec
    
    if any(['red_noise' in x for x in p_dict.keys()]):
        rn_model = gp_priors.powerlaw(log10_A=log10_A_rn,
                            gamma=gamma_rn)

        rn = gp_signals.FourierBasisGP(rn_model, components=120, name='red_noise')
        s_all[p] += rn
    
    """if any(['n_earth' in x for x in p_dict.keys()]):
        deter_sw = solar_wind(n_earth=n_earth)
        mean_sw = deterministic_signals.Deterministic(deter_sw, name='n_earth')
        s_all[p] += mean_sw

    if any(['gp_sw' in x for x in p_dict.keys()]):
        Tspan = psr[p].toas.max() - psr[p].toas.min()
        sw_components = 120  
        sw_prior = utils.powerlaw(log10_A=log10_A_sw, gamma=gamma_sw)
        sw_basis = createfourierdesignmatrix_solar_dm(nmodes=sw_components, Tspan=Tspan)
        sw = gp_signals.BasisGP(sw_prior, sw_basis, name='gp_sw')
        #sw_spectrum = gp_priors.free_spectrum(log10_rho=log10_rho_sw)
        #sw_basis = createfourierdesignmatrix_solar_dm(nmodes=sw_components, Tspan=Tspan)
        #sw = gp_signals.BasisGP(sw_spectrum, sw_basis, name='sw_specturm')
        s_all[p] += sw"""

    if any(['dm_gp' in x for x in p_dict.keys()]): 
        Tspan = psr[p].toas.max() - psr[p].toas.min()
        dm = dm_noise(log10_A=log10_A_dm,gamma=gamma_dm,Tspan=Tspan,components=120,option="powerlaw")  
        s_all[p] += dm

    if any(['chrom_gp' in x for x in p_dict.keys()]):
        chrom_model = utils.powerlaw(log10_A=log10_A_chrom_prior,
                            gamma=gamma_chrom_prior)
        if any(['chrom_gp_idx' in x for x in p_dict.keys()]):
            chrom_basis_idx = gp_bases.createfourierdesignmatrix_chromatic(nmodes=120,
                                                                        idx=idx)

            chrom_idx = gp_signals.BasisGP(chrom_model, chrom_basis_idx, name='chrom_gp')
            s_all[p] += chrom_idx
        else :
            chrom_basis = gp_bases.createfourierdesignmatrix_chromatic(nmodes=120,
                                                    idx=4)
            chrom = gp_signals.BasisGP(chrom_model, chrom_basis, name='chrom_gp')
            s_all[p] += chrom

    if any(['chrom1yr' in x for x in p_dict.keys()]):
        s_all[p] += chrom1yr
    if any(['chrom_bump' in x for x in p_dict.keys()]):
        s_all[p] += chrom_bump



###################################################################################################################
mods = []
for p in psrnames:
    mods.append(s_all[p](psr[p]))

pta = signal_base.PTA(mods)

## Set value of constant parameters #######
#with open('/fred/oz002/users/akulkarn/MPTA_17April24/sim_17April_apptainer_V2/chains/'+gw_mod+'/noisefile_{}_{}.json'.format(inj_mod,med_map),'r') as fp:
#    noisedict = json.load(fp)

"""with open('/fred/oz002/users/smishra/work/PhD/RM_pat_studies/RM_measurement/enterprise/simulations/postCoC/saurav_realistic_PTA/heirarch_values.json','r') as fp:
    noisedict = json.load(fp)"""
noisedict = Noise_MPTA

#print(noisedict)
pta.set_default_params(noisedict)




#################### PTMCMC Block ###################################################################
# x0 = np.hstack([p.sample() for p in pta.params])
# ndim = len(x0)

# N = int(3e5)

# cov = np.diag(np.ones(ndim) * 0.01**2)

# outdir = os.path.join("/fred/oz002/users/akulkarn/MPTA_17April24/sim_17April_apptainer_V2/chains" , str(chainnum), str(num))

# sampler = ptmcmc(ndim, pta.get_lnlikelihood, pta.get_lnprior, cov,
#                  outDir=outdir, resume=False)

# print(pta.param_names)
# filename = outdir + "/pars.txt"
# if os.path.exists(filename):
#     os.remove(filename)
# with open(filename, "a") as f:
#     for par in pta.param_names:
#         f.write(par + '\n')

# sampler.sample(x0, N, SCAMweight=30, AMweight=15, DEweight=50)
# ##########################################################################################################

############################ Hypermodel block ####################################################

# set up PTA
"""nmodels = 1
ptah = dict.fromkeys(np.arange(nmodels))
ptah[0] = signal_base.PTA(mods)
ptah[0].set_default_params(noisedict)
hyper_model = hypermodel.HyperModel(ptah)"""


nmodels = 1
pta = dict.fromkeys(np.arange(nmodels))
pta[0] = signal_base.PTA(mods)
hyper_model = hypermodel.HyperModel(pta)

# set initial parameters drawn from prior
x0 = hyper_model.initial_sample()
ndim = len(x0)

# sampler for N steps
#N = int(1e5)
N = int(1e6)
# output directory:

#outdir = os.path.join("/fred/oz002/users/akulkarn/MPTA_17April24/sim_17April_apptainer_V2/chains" , str(chainnum), 'Grp{}'.format(grp), str(num))
#outdir = os.path.join("/fred/oz002/users/akulkarn/MPTA_17April24/sim_17April_apptainer_V2/chains" , str(chainnum), str(num))
#outdir = '/fred/oz002/users/smishra/work/PhD/RM_pat_studies/RM_measurement/enterprise/simulations/postCoC/saurav_realistic_PTA/new_app/chain_realistic_pta_IPS_gwb_fixedgamma' + "/crn" + "_" + chainnum
#outdir = '/fred/oz005/users/smishra/work/enterprise/new_app/chain_realistic_pta_IPS_gwb_fixedgamma' + "/crn" + "_" + chainnum
outdir = os.path.join('/fred/oz002/users/mbailes/astral/timing2025/chains', dirname, f'crn_{chainnum}')

print (outdir)
# Use PTMCMC sampler. We can easily update this to use e.g. Bilby instead
sampler = hyper_model.setup_sampler(outdir=outdir, resume=True)
os.system('cp {0} {1}/ '.format(sys.argv[0], outdir))
# Print parameter names and write to a file
print(hyper_model.param_names)
filename = outdir + "/pars.txt"
if os.path.exists(filename):
    os.remove(filename)
with open(filename, "a") as f:
    for par in hyper_model.param_names:
        f.write(par + '\n')

# Sample! The sampler parameters can be left as default.
sampler.sample(x0, N, SCAMweight=30, AMweight=15, DEweight=50)








# # ############################ Bilby Block #################
# priors = bilby_warp.get_bilby_prior_dict(pta)
# parameters = dict.fromkeys(priors.keys())
# likelihood = bilby_warp.PTABilbyLikelihood(pta,parameters)

# outdir = os.path.join("/fred/oz002/users/akulkarn/MPTA_Noise/chains" , str(chainnum), str(num), "bilby/") 
# label = psrname

# results = bilby.run_sampler(likelihood=likelihood, priors=priors, outdir=outdir, label=label, sampler='dynesty', clean=False, resume=True, nlive=1000, npool=1, verbose=True)
# results.plot_corner()