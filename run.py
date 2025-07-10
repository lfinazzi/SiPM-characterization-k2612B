import os
os.chdir('C:/Users/LINE/Desktop/LabOSat CAC')

from k2612B import run, stationary_check

encapsulado = 5
T           = 2
average_temp = 17

group_path  = 'Encapsulado_%s_temp//%s//' % (encapsulado, T)
plotFlag    = 1
saveFlag    = 1

#stationary_check(encapsulado, T, saveFlag)
run(1, 'LabOSat', average_temp, group_path, plotFlag, saveFlag)    
    

#%% Standalone Tests
from tests import SiPMDelay
from setup import setup
from functions import gpib, clear_all, error_V, error_I
import os
import matplotlib.pyplot as plt

clear_all()

os.chdir('C:/Users/LINE/Desktop/LabOSat CAC')

[smu_2612b, rm] = gpib(24)
config = setup()

encapsulado = 4
measurement = 1

time_sipm, I_sipm, time_led, V_led, I_led = SiPMDelay(smu_2612b, config, encapsulado, measurement)

smu_2612b.close()

V_led_err = error_V(V_led, '2602', source=False)
I_sipm_err = error_I(I_sipm, '2602', source=False)

I_sipm_g = [1E6*i for i in I_sipm]
I_sipm_err_g = [1E6*i for i in I_sipm_err]

plt.figure(3)
plt.errorbar(time_led, V_led, yerr=V_led_err, fmt='.k', capsize=3)
plt.xlabel("Time [s]")
plt.ylabel("LED Voltage [V]")
plt.grid(True)
plt.tight_layout(True)

plt.figure(4)
plt.errorbar(time_sipm, I_sipm_g, yerr=I_sipm_err_g, fmt='.k', capsize=3)
plt.xlabel("Time [s]")
plt.ylabel("SiPM Current [uA]")
plt.grid(True)
plt.tight_layout(True)
