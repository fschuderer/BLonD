# coding: utf8
# Copyright 2014-2017 CERN. This software is distributed under the
# terms of the GNU General Public Licence version 3 (GPL Version 3), 
# copied verbatim in the file LICENCE.md.
# In applying this licence, CERN does not waive the privileges and immunities 
# granted to it by virtue of its status as an Intergovernmental Organization or
# submit itself to any jurisdiction.
# Project website: http://blond.web.cern.ch/

'''
Test case to show how to use phase loop (CERN PS Booster context).

:Authors: **Danilo Quartullo**
'''

from __future__ import division, print_function
import numpy as np
from input_parameters.ring import Ring
from input_parameters.rf_parameters import RFStation
from trackers.tracker import RingAndRFTracker, FullRingAndRF
from beam.distributions import matched_from_distribution_function
from monitors.monitors import BunchMonitor
from beam.profile import Profile, CutOptions
from beam.beam import Beam, Proton
from plots.plot import Plot
from llrf.beam_feedback import BeamFeedback

# Beam parameters
n_macroparticles = 100000
n_particles = 0


# Machine and RF parameters
radius = 25 # [m]
gamma_transition = 4.076750841
alpha = 1 / gamma_transition**2
C = 2*np.pi*radius  # [m]     
n_turns = 500
general_params = Ring(C, alpha, 310891054.809, 
                                   Proton(), n_turns)

# Cavities parameters
n_rf_systems = 1                                     
harmonic_numbers_1 = 1
voltage_1 = 8000  # [V]  
phi_offset_1 = np.pi   # [rad]
rf_params = RFStation(general_params, n_rf_systems,
                                [harmonic_numbers_1], [voltage_1], [phi_offset_1])

my_beam = Beam(general_params, n_macroparticles, n_particles)


cut_options = CutOptions(cut_left= 0, cut_right=2*np.pi, n_slices=200, 
                         RFSectionParameters=rf_params, cuts_unit = 'rad')
slices_ring = Profile(my_beam, cut_options)

#Phase loop
configuration = {'machine': 'PSB', 'PL_gain': 1./25.e-6, 'period': 10.e-6}
phase_loop = BeamFeedback(general_params, rf_params, slices_ring, configuration)


#Long tracker
long_tracker = RingAndRFTracker(rf_params, my_beam, periodicity='Off',
                                BeamFeedback=phase_loop)

full_ring = FullRingAndRF([long_tracker])


distribution_type = 'gaussian'
bunch_length = 200.0e-9
distribution_variable = 'Action'

matched_from_distribution_function(my_beam, full_ring, 
                                   bunch_length=bunch_length,
                                   distribution_type=distribution_type, 
                                   distribution_variable=distribution_variable, seed=1222)
                                   
my_beam.dE += 90.0e3
slices_ring.track()

#Monitor
bunch_monitor = BunchMonitor(general_params, rf_params, my_beam,
                             '../output_files/EX_08_output_data',
                             Profile=slices_ring, PhaseLoop=phase_loop)


#Plots
format_options = {'dirname': '../output_files/EX_08_fig'}
plots = Plot(general_params, rf_params, my_beam, 50, n_turns, 0.0, 2*np.pi,
             -1e6, 1e6, xunit='rad', separatrix_plot=True, Profile=slices_ring,
             format_options=format_options,
             h5file='../output_files/EX_08_output_data', PhaseLoop=phase_loop)

# Accelerator map
map_ = [full_ring] + [slices_ring] + [bunch_monitor] + [plots] 


for i in range(1, n_turns+1):
    print(i)
    
    for m in map_:
        m.track()      
    
print("Done!")
