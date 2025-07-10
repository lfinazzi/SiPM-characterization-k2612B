import os
import matplotlib.pyplot as plt
import time
import numpy as np

home_path = "C:/Users/LINE/Desktop/LabOSat CAC/"
os.chdir(home_path)

from functions import gpib, readBuffer

[smu_2612b, rm] = gpib(26)


i_initial = 0
i_end = 23E-3
     

smu_2612b.write('reset()')
smu_2612b.write('smua.reset()')
smu_2612b.write('errorqueue.clear()')


smu_2612b.write('format.data = format.ASCII')


# Buffer operations -------------------------------------------------------

smu_2612b.write('smua.nvbuffer1.clear()')

smu_2612b.write('smua.nvbuffer1.appendmode = 1')

# could try to measure 50 points instead of 100 in Vbr measurement
smu_2612b.write('smua.nvbuffer1.fillcount = ' + str(200))  

smu_2612b.write('smua.nvbuffer1.collectsourcevalues = 1')

smu_2612b.write('smua.measure.count = 1')

smu_2612b.write('smua.nvbuffer1.clear()')


# -------------------------------------------------------------------------   
# smua configuration (SiPM)

smu_2612b.write('smua.source.func = smua.OUTPUT_DCAMPS')
smu_2612b.write('display.smua.measure.func = display.MEASURE_DCVOLTS')

smu_2612b.write('smua.source.autorangei = smua.AUTORANGE_ON')
smu_2612b.write('smua.measure.autorangev = smua.AUTORANGE_ON')

#compliance values for I and V
smu_2612b.write('smua.source.limiti = 0.006')
smu_2612b.write('smua.source.limitv = 3')
	
smu_2612b.write('smua.measure.nplc = 1')

smu_2612b.write('smua.measure.delay = 0.01')


b = np.arange(0, 200, 1)
i_led_values = [i_initial + (i_end - i_initial)/(200.0)*i for i in b]

smu_2612b.write('smua.source.output = smua.OUTPUT_ON')

print("Start of SiPM IV measurement\n")


for j in range(len(i_led_values)):
    
    smu_2612b.write('smua.source.leveli = ' + str(i_led_values[j]))
    smu_2612b.write('smua.measure.v(smua.nvbuffer1)')
    
    time.sleep(0.01 + 1/50.0)
    
smu_2612b.write('smua.source.output = smua.OUTPUT_OFF')

print("End of SiPM IV measurement\n")

time.sleep(3)

readingsV, readingsI = readBuffer(smu_2612b, 'a')
    
    
plt.plot(readingsV, readingsI, 'o')
#plt.yscale('log')
#np.savetxt("Zener_IV_curve_23mA.txt", np.c_[readingsV, readingsI])
    
    
