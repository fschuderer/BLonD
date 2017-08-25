# coding: utf8
# Copyright 2014-2017 CERN. This software is distributed under the
# terms of the GNU General Public Licence version 3 (GPL Version 3),
# copied verbatim in the file LICENCE.md.
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization or
# submit itself to any jurisdiction.
# Project website: http://blond.web.cern.ch/

'''
**Filters and methods for control loops**

:Authors: **Helga Timko**
'''

from __future__ import division
import numpy as np
from scipy.constants import c

# Set up logging
import logging
logger = logging.getLogger(__name__)



# def rectangle(t, tau):
#     r"""Rectangular function of time
#     
#     .. math:: \mathsf{rect} \left( \frac{t}{\tau} \right) = 
#         \begin{cases}
#             1 \, , \, t \in (-\tau/2, \tau/2) \\
#             0.5 \, , \, t = \pm \tau/2 \\
#             0 \, , \, \textsf{otherwise}
#         \end{cases}
#         
#     Parameters
#     ----------
#     t : float array
#         Time array
#     tau : float
#         Time window of rectangular function
#         
#     Returns
#     -------
#     float array
#         Rectangular function for given time array
#         
#     """
#     
#     dt = t[1] - t[0]
#     limits = np.where((np.fabs(t - tau/2) < dt/2) | 
#                       (np.fabs(t + tau/2) < dt/2))[0]
#     logger.debug("In rectangle(), number of limiting indices is %d" 
#                  %(len(limits)))
#     print(limits)
#     if len(limits) != 2:
#         raise RuntimeError("ERROR in impulse_response.rectangle(): time" +
#                            " array not in correct range!")
#     y = np.zeros(len(t))
#     y[limits] = 0.5
#     y[limits[0]+1:limits[1]] = np.ones(limits[1] - limits[0] - 1)
# 
#     return y
# 
# 
# 
def rectangle(t, tau):
    r"""Rectangular function of time
    
    .. math:: \mathsf{rect} \left( \frac{t}{\tau} \right) = 
        \begin{cases}
            1 \, , \, t \in (-\tau/2, \tau/2) \\
            0.5 \, , \, t = \pm \tau/2 \\
            0 \, , \, \textsf{otherwise}
        \end{cases}
        
    Parameters
    ----------
    t : float array
        Time array
    tau : float
        Time window of rectangular function
        
    Returns
    -------
    float array
        Rectangular function for given time array
        
    """
    
    dt = t[1] - t[0]
    llimit = np.where(np.fabs(t + tau/2) < dt/2)[0]
    ulimit = np.where(np.fabs(t - tau/2) < dt/2)[0]
    if len(llimit) != 1:
        raise RuntimeError("ERROR in impulse_response.rectangle(): time" +
                           " array doesn't start at rising edge!")
    if len(ulimit) not in [0,1]:
        raise RuntimeError("ERROR in impulse_response.rectangle(): time" +
                           " array has multiple falling edges!")
    logger.debug("In rectangle(), index of rising edge is %d" %llimit[0])
    y = np.zeros(len(t))
    y[llimit[0]] = 0.5
    if len(ulimit) == 1:
        y[llimit[0]+1:ulimit[0]] = np.ones(ulimit[0] - llimit[0] - 1)
        y[ulimit[0]] = 0.5
    else:
        y[llimit[0]+1:] = 1
    
    return y



# def triangle(t, tau):
#     r"""Triangular function of time
#     
#     .. math:: \mathsf{tri} \left( \frac{t}{\tau} \right) = 
#         \begin{cases}
#             1 - \frac{t}{\tau}\, , \, t \in (0, \tau) \\
#             0.5 \, , \, t = 0 \\
#             0 \, , \, \textsf{otherwise}
#         \end{cases}
#         
#     Parameters
#     ----------
#     t : float array
#         Time array
#     tau : float
#         Time window of rectangular function
#         
#     Returns
#     -------
#     float array
#         Triangular function for given time array
#         
#     """
#     
#     dt = t[1] - t[0]
#     limits = np.where(np.fabs(t) < dt/2)[0]
#     logger.debug("In triangle(), number of limiting indices is %d" 
#                  %(len(limits)))
#     print(limits)
#     if len(limits) != 1:
#         raise RuntimeError("ERROR in impulse_response.triangle(): time" +
#                            " array not in correct range!")
#     y = np.zeros(len(t))
#     y[limits[0]] = 0.5
#     y[limits[0]+1:] = 1 - t[limits[0]+1:]/tau
#     y[np.where(y < 0)[0]] = 0
# 
#     return y
# 
# 
#
def triangle(t, tau):
    r"""Triangular function of time
    
    .. math:: \mathsf{tri} \left( \frac{t}{\tau} \right) = 
        \begin{cases}
            1 - \frac{t}{\tau}\, , \, t \in (0, \tau) \\
            0.5 \, , \, t = 0 \\
            0 \, , \, \textsf{otherwise}
        \end{cases}
        
    Parameters
    ----------
    t : float array
        Time array
    tau : float
        Time window of rectangular function
        
    Returns
    -------
    float array
        Triangular function for given time array
        
    """
    
    dt = t[1] - t[0]
    llimit = np.where(np.fabs(t) < dt/2)[0]
    logger.debug("In triangle(), index of rising edge is %d" %llimit[0])
    if len(llimit) != 1:
        raise RuntimeError("ERROR in impulse_response.triangle(): time" +
                           " array doesn't start at rising edge!")
    y = np.zeros(len(t))
    y[llimit[0]] = 0.5
    y[llimit[0]+1:] = 1 - t[llimit[0]+1:]/tau
    y[np.where(y < 0)[0]] = 0

    return y



class TravellingWaveCavity(object):
    r"""Impulse responses of a travelling wave cavity. The induced voltage 
    :math:`V(t)` from the impulse response :math:`h(t)` and the I,Q (cavity or
    generator) current :math:`I(t)` can be written in matrix form,
    
    .. math:: 
        \left( \begin{matrix} V_I(t) \\ 
        V_Q(t) \end{matrix} \right)
        = \left( \begin{matrix} h_s(t) & - h_c(t) \\
        h_c(t) & h_s(t) \end{matrix} \right)
        * \left( \begin{matrix} I_I(t) \\ 
        I_Q(t) \end{matrix} \right) \, ,
        
    where :math:`*` denotes convolution, 
    :math:`h(t)*x(t) = \int d\tau h(\tau)x(t-\tau)`. 
    
    For the **cavity-to-beam induced voltage**, we define
    
    .. math:: 
        R_b \equiv \frac{\rho l^2}{8} \, 
    
    where :math:`\rho` is the series impedance, :math:`l` the accelerating
    length, :math:`\tau` the filling time. The cavity-to-beam wake is 
    
    .. math::
        W_b(t) = \frac{4 R_b}{\tau} \mathsf{tri}\left(\frac{t}{\tau}\right) \cos(\omega_r t)
    
    and the impulse response components are
    
    .. math::
        h_{s,b}(t) &= \frac{2 R_b}{\tau} \mathsf{tri}\left(\frac{t}{\tau}\right) \cos((\omega_c - \omega_r)t) \, , \\
        h_{c,b}(t) &= \frac{2 R_b}{\tau} \mathsf{tri}\left(\frac{t}{\tau}\right) \sin((\omega_c - \omega_r)t) \, ,
        
    where :math:`\mathsf{tri}(x)` is the triangular function, :math:`\omega_r`
    is the central revolution frequency of the cavity, and :math:`\omega_c` is
    the carrier revolution frequency of the I,Q demodulated current signal. On
    the carrier frequency, :math:`\omega_c = \omega_r`,
    
    .. math::
        h_{s,b}(t) &= \frac{2 R_b}{\tau} \mathsf{tri}\left(\frac{t}{\tau}\right) \\
        h_{c,b}(t) &= 0 \, .
     
    For the **cavity-to-generator induced voltage**, we define
    
    .. math:: 
        R_g \equiv l \sqrt{\frac{\rho Z_0}{2}} \, 
    
    where :math:`Z_0` is the shunt impedance when measuring the generator 
    current; assumed to be 50 :math:`\Omega`. The cavity-to-generator wake is 
    
    .. math::
        W_g(t) = \frac{2 R_g}{\tau} \mathsf{rect}\left(\frac{t}{\tau}\right) \cos(\omega_r t)
    
    and the impulse response components are
    
    .. math::
        h_{s,g}(t) &= \frac{R_g}{\tau} \mathsf{rect}\left(\frac{t}{\tau}\right) \cos((\omega_c - \omega_r)t) \, , \\
        h_{c,g}(t) &= \frac{R_g}{\tau} \mathsf{rect}\left(\frac{t}{\tau}\right) \sin((\omega_c - \omega_r)t) \, ,
        
    where :math:`\mathsf{rect}(x)` is the rectangular function. On the carrier
    frequency, :math:`\omega_c = \omega_r`,
    
    .. math::
        h_{s,g}(t) &= \frac{R_g}{\tau} \mathsf{rect}\left(\frac{t}{\tau}\right) \\
        h_{c,g}(t) &= 0 \, .
    
    Parameters
    ----------
    l_cell : float
        Cavity cell length [m]
    N_cells : int
        Number of accelerating (interacting) cells in a cavity
    rho : float
        Series impedance [Ohms/m^2] of the cavity
    v_g : float
        Group velocity [c] in units of the speed of light
    omega_r : flaot
        Central (resonance) revolution frequency [1/s] of the cavity
        
    Attributes
    ----------
    Z_0 : float
        Shunt impedance of generator current measurement; assumed to be 50 Ohms
    l_cav : float
        Length [m] of the interaction region
    tau : float
        Cavity filling time [s]
        
    """
        
    def __init__(self, l_cell, N_cells, rho, v_g, omega_r):
        
        self.l_cell = float(l_cell)
        self.N_cells = int(N_cells)
        self.rho = float(rho)
        if v_g > 0 and v_g < 1:
            self.v_g = float(v_g)
        else:
            raise RuntimeError("ERROR in TravellingWaveCavity: group" +
                " velocity out of limits (0,1)!")
        self.omega_r = float(omega_r)
        
        # Assumed impedance for measurement of generator current
        self.Z_0 = 50
        
        # Calculated
        self.l_cav = float(self.l_cell*self.N_cells)
        self.tau = self.l_cav/(self.v_g*c)*(1 + self.v_g) # v_g opposite to wave!
        
        # Set up logging
        self.logger = logging.getLogger(__class__.__name__)
        self.logger.info("Class initialized")
        self.logger.debug("Filling time %.4e s", self.tau)
        
        
#     def impulse_response(self, omega_c, time):
#         """Impulse response from the cavity towards the beam and towards the 
#         generator. For a signal that is I,Q demodulated at a given carrier 
#         frequency :math:`\omega_c`. The formulae assume that the carrier 
#         frequency is be close to the central frequency 
#         :math:`\omega_c/\omega_r \ll 1` and that the signal is low-pass
#         filtered (i.e.\ high-frequency components can be neglected).
#          
#         Parameters
#         ----------
#         omega_c : float
#             Carrier revolution frequency [1/s]
#         time : float
#             Time array to act on
#              
#         Attributes
#         ----------
#         d_omega : float
#             :math:`\omega_c - \omega_r` [1/s]
#         R_beam : float
#             :math:`R_b` [\Omega] as defined above
#         R_gen : float
#             :math:`R_g` [\Omega] as defined above
#         W_beam : float array
#             :math:`W_b(t)` [\Omega/s] as defined above
#         W_gen : float array
#             :math:`W_g(t)` [\Omega/s] as defined above
#         hs_beam : float array
#             :math:`h_{s,b}(t)` [\Omega/s] as defined above
#         hc_beam : float array
#             :math:`h_{c,b}(t)` [\Omega/s] as defined above
#         hs_gen : float array
#             :math:`h_{s,g}(t)` [\Omega/s] as defined above
#         hc_gen : float array
#             :math:`h_{c,g}(t)` [\Omega/s] as defined above
#  
#         """
#          
#         self.omega_c = float(omega_c)
#         self.d_omega = self.omega_c - self.omega_r
#         if np.fabs((self.d_omega)/self.omega_r) > 0.1:
#             raise RuntimeError("ERROR in TravellingWaveCavity" +
#                 " impulse_response(): carrier frequency should be close to" +
#                 " central frequency of the cavity!")
#      
#         self.time = time
#          
#         # Shunt impedances towards beam and generator
#         self.R_beam = 0.125*self.rho*self.l_cav**2
#         self.R_gen = self.l_cav*np.sqrt(0.5*self.rho*self.Z_0)
#  
#         # Impulse response if on carrier frequency
#         self.hs_beam = 2*self.R_beam/self.tau*triangle(time, self.tau)
#         self.hc_beam = None
#         self.hs_gen = self.R_gen/self.tau*rectangle(time, self.tau)
#         self.hc_gen = None
#  
#         # Wake fields towards beam and generator
#         self.W_beam = 2*np.copy(self.hs_beam)*np.cos(self.omega_r*self.time)
#         self.W_gen = 2*np.copy(self.hs_gen)*np.cos(self.omega_r*self.time)
#                 
#         # Impulse response if not on carrier frequency
#         if np.fabs((self.d_omega)/self.omega_r) > 1e-12:
#             self.hc_beam = np.copy(self.hs_beam)*np.sin(self.d_omega*self.time)
#             self.hs_beam *= np.cos(self.d_omega*self.time)
#             self.hc_gen = np.copy(self.hs_gen)*np.sin(self.d_omega*self.time)
#             self.hs_gen *= np.cos(self.d_omega*self.time)
#  
#                  
    def impulse_response(self, omega_c, time):
        """Impulse response from the cavity towards the beam and towards the 
        generator. For a signal that is I,Q demodulated at a given carrier 
        frequency :math:`\omega_c`. The formulae assume that the carrier 
        frequency is be close to the central frequency 
        :math:`\omega_c/\omega_r \ll 1` and that the signal is low-pass
        filtered (i.e.\ high-frequency components can be neglected).
         
        Parameters
        ----------
        omega_c : float
            Carrier revolution frequency [1/s]
        time : float
            Time array to act on
             
        Attributes
        ----------
        d_omega : float
            :math:`\omega_c - \omega_r` [1/s]
        R_beam : float
            :math:`R_b` [\Omega] as defined above
        R_gen : float
            :math:`R_g` [\Omega] as defined above
        W_beam : float array
            :math:`W_b(t)` [\Omega/s] as defined above
        W_gen : float array
            :math:`W_g(t)` [\Omega/s] as defined above
        hs_beam : float array
            :math:`h_{s,b}(t)` [\Omega/s] as defined above
        hc_beam : float array
            :math:`h_{c,b}(t)` [\Omega/s] as defined above
        hs_gen : float array
            :math:`h_{s,g}(t)` [\Omega/s] as defined above
        hc_gen : float array
            :math:`h_{c,g}(t)` [\Omega/s] as defined above
 
        """
         
        self.omega_c = float(omega_c)
        self.d_omega = self.omega_c - self.omega_r
        if np.fabs((self.d_omega)/self.omega_r) > 0.1:
            raise RuntimeError("ERROR in TravellingWaveCavity" +
                " impulse_response(): carrier frequency should be close to" +
                " central frequency of the cavity!")
     
#         self.dt = dt
#         n = np.min([int(self.tau/self.dt), self.pro])
#         if n < 3:
#             raise RuntimeError("ERROR in TravellingWaveCavity" +
#                 " impulse_response(): time resolution insufficient!")
#         self.t_beam = np.linspace(0., n*self.dt, n, endpoint=True) 
#         self.t_gen = np.linspace(-0.5*self.tau, n*self.dt, n, endpoint=True) 
        self.t_beam = time - time[0]
        self.t_gen = time - time[0] - 0.5*self.tau
         
         
        # Shunt impedances towards beam and generator
        self.R_beam = 0.125*self.rho*self.l_cav**2
        self.R_gen = self.l_cav*np.sqrt(0.5*self.rho*self.Z_0)
 
        # Impulse response if on carrier frequency
        self.hs_beam = 2*self.R_beam/self.tau*triangle(self.t_beam, self.tau)
        self.hc_beam = None
        self.hs_gen = self.R_gen/self.tau*rectangle(self.t_gen, self.tau)
        self.hc_gen = None
 
        # Wake fields towards beam and generator
        self.W_beam = 2*np.copy(self.hs_beam)*np.cos(self.omega_r*self.t_beam)
        self.W_gen = 2*np.copy(self.hs_gen)*np.cos(self.omega_r*self.t_gen)
                
        # Impulse response if not on carrier frequency
        if np.fabs((self.d_omega)/self.omega_r) > 1e-12:
            self.hc_beam = np.copy(self.hs_beam)*np.sin(self.d_omega*self.t_beam)
            self.hs_beam *= np.cos(self.d_omega*self.t_beam)
            self.hc_gen = np.copy(self.hs_gen)*np.sin(self.d_omega*self.t_gen)
            self.hs_gen *= np.cos(self.d_omega*self.t_gen)
 


class SPS4Section200MHzTWC(TravellingWaveCavity):
        
    def __init__(self):        
        
        TravellingWaveCavity.__init__(self, 0.374, 43, 2.71e4, 0.0946,
                                      2*np.pi*200.222e6)
        

class SPS5Section200MHzTWC(TravellingWaveCavity):
        
    def __init__(self):        
        
        TravellingWaveCavity.__init__(self, 0.374, 54, 2.71e4, 0.0946, 
                                      2*np.pi*200.222e6)
    