from functions import clear_all, gpib, plot, save_iv, save_dark, save_led, split, readBuffer, P, Vbr
from setup import setup
from tests import IVComplete, DarkCurrent, LEDTest
import time
import winsound
import os

def run(n, test, average_temp, group_path, plotFlag, saveFlag):

    clear_all()
    # Loading setups configurations
    config = setup()
    
    breakdown = Vbr(average_temp)
    
    #rm-list_resources() to find address for smu
    address_2612b = 26
    
    #running tests (smua measures iv and smub measures r)
    
    [smu_2612b, rm]  = gpib(address_2612b)
    
    winsound.Beep(750, 750)
    
    v_bias = [28.8, 29.4, 29.5, 29.6, 29.7, 29.8, 29.9, 30.0]
    
    for j in range(0, len(v_bias)):
        
        # ---------------------------------------------------------------------
        # TEST ----------------------------------------------------------------    
    
        [readingsI_sipm_led, readingsI_led, readingsV_led] = LEDTest(smu_2612b, config, v_bias[j])
           
        # ---------------------------------------------------------------------


        if plotFlag == 1:
            graphIV_led = plot(readingsI_led[1:-1], readingsI_sipm_led[1:-1], 'Iled', 'Isipm', 1, log=True, errorbars_2602=True, xflag='I')
        else:
            graphIV_led = 'NULL'  
        
        if saveFlag == 1:
            group_path_dark = group_path + "LED\\Bias_%sV" % v_bias[j]
            save_led(readingsI_sipm_led, readingsI_led, readingsV_led, graphIV_led, 1, group_path_dark)
        
        #sleep time = 10s for 9.7k resistor in parallel
        time.sleep(1)
        
    # withour R or zener, optimal wait time is 20 s, with zener, it is 40 s
    #time.sleep(180)
    
    number = []
    for g in range(0, 125):
        number.append(g)
    
    # ---------------------------------------------------------------------
    # TEST ----------------------------------------------------------------
    
    for j in range(0, 4):
        
        if j == 3:
            winsound.Beep(750, 750)
        
        V_bias = 30
    
        readingsI_sipm_dark = DarkCurrent(smu_2612b, config, V_bias)
        
        # ---------------------------------------------------------------------
        
        if plotFlag == 1:
            graphIV = plot(number, readingsI_sipm_dark, 'N', 'Isipm', 4, log=False, errorbars_2602=True)
        else:
            graphIV = 'NULL'  
        
        if saveFlag == 1:
            group_path_dark = group_path + "idark\\Bias_%sV" % V_bias
            save_dark(readingsI_sipm_dark, graphIV, j + 1, group_path_dark)
    
    
    winsound.Beep(750, 750)
    for j in range(0, 5):
        
        # ---------------------------------------------------------------------
        # TEST ----------------------------------------------------------------
        
        [readingsV_sipm, readingsI_sipm] = IVComplete(smu_2612b, config, breakdown)
        
        # ---------------------------------------------------------------------
        
        readingsV_sipm_neg, readingsV_sipm_pos, readingsI_sipm_neg, readingsI_sipm_pos = split(readingsV_sipm, readingsI_sipm)
    
        
        if plotFlag == 1:
            graphIV_neg = plot(readingsV_sipm_neg, readingsI_sipm_neg, 'V', 'Isipm', 2, log=False, errorbars_2602=True)
            graphIV_pos = plot(readingsV_sipm_pos, readingsI_sipm_pos, 'V', 'Isipm', 3, log=False, errorbars_2602=True)
        
        else:
            graphIV_neg = 'NULL'
            graphIV_pos = 'NULL'
        
        if saveFlag == 1:
            group_path_pos = group_path + "rq"
            group_path_neg = group_path + "vbr"
            save_iv(readingsV_sipm_neg, readingsI_sipm_neg, graphIV_neg, j + 1, group_path_pos)
        
            save_iv(readingsV_sipm_pos, readingsI_sipm_pos, graphIV_pos, j + 1, group_path_neg)
     

    smu_2612b.close()
    
    return


def stationary_check(encapsulado, T, saveFlag):
    """
    
    
    
    ---------
    
    """
    
    import numpy as np
    
    clear_all()
    
    # Loading setups configurations
    config = setup()
    
    #rm-list_resources() to find address for smu
    address_2612b = 26
    
    
    [smu_2612b, rm]  = gpib(address_2612b)
    
    if saveFlag == 1:
        if not os.path.exists('.\\results\\Encapsulado_%s_temp\\%s\\Transitorio' % (encapsulado, T)):
            os.makedirs('.\\results\\Encapsulado_%s_temp\\%s\\Transitorio' % (encapsulado, T))

    
    [i_cc_sipm,
    v_cc_sipm,
    i_rang_sipm,
    v_rang_sipm,
    v_level_sipm,
    _,
    _,
    _,
    _,
    _,
    N,
    points,
    delay,
    _] = config
     
     
    tolerance = 1.25*P('n')
    NPLC = 25
    
    smu_2612b.write('reset()')
    smu_2612b.write('smua.reset()')
    smu_2612b.write('smub.reset()')
    smu_2612b.write('errorqueue.clear()')
    
    
    smu_2612b.write('format.data = format.ASCII')
    

    # Buffer operations -------------------------------------------------------
    
    smu_2612b.write('smua.nvbuffer1.clear()')
    
    smu_2612b.write('smua.nvbuffer1.appendmode = 1')
    
    smu_2612b.write('smua.nvbuffer1.fillcount = ' + str(10*N))  
    
    smu_2612b.write('smua.nvbuffer1.collectsourcevalues = 1')

    smu_2612b.write('smua.measure.count = 1')
    
    smu_2612b.write('smua.nvbuffer1.clear()')
    

    # -------------------------------------------------------------------------   
    # smua configuration (SiPM)
    
    smu_2612b.write('smua.source.func = smua.OUTPUT_DCVOLTS')
    smu_2612b.write('display.smua.measure.func = display.MEASURE_DCAMPS')
    
    if (i_rang_sipm == 'AUTO'):
        smu_2612b.write('smua.source.autorangei = smua.AUTORANGE_ON')
    else:
        smu_2612b.write('smua.source.rangei = ' + str(i_rang_sipm))
    
    if (v_rang_sipm == 'AUTO'):
        smu_2612b.write('smua.measure.autorangev = smua.AUTORANGE_ON')
    else:
        smu_2612b.write('smua.measure.rangev = ' + str(v_rang_sipm))

    #compliance values for I and V
    smu_2612b.write('smua.source.limiti = ' + str(i_cc_sipm))
    smu_2612b.write('smua.source.limitv = ' + str(v_cc_sipm))
	
    smu_2612b.write('smua.measure.nplc = ' + str(NPLC))
    
    smu_2612b.write('smua.measure.delay = ' + str(delay))
    
    smu_2612b.write('smua.source.levelv = 30')
        

    smu_2612b.write('smua.source.output = smua.OUTPUT_ON') 
    flag = False
    
    print("Detecting stationary regime\n\n")
    j = 1
    startTime = time.time()
    time_v = []
    while not flag:
        
        print("Try: " + str(j))
        for i in range(0, 20):
            smu_2612b.write('smua.measure.i(smua.nvbuffer1)')
            t = time.time() - startTime
            time_v.append(t)
            time.sleep(delay + NPLC/50.0)
            
        smu_2612b.write('waitcomplete()') 
        time.sleep(1)

        readingsI = readBuffer(smu_2612b, 'a', source_values=False)
            
            
        plot(time_v, readingsI, "t", "I", j, errorbars_2602=True)
        

        print("Std. dev: " + str(np.std(readingsI[-20:])))
            
        if np.std(readingsI[-20:]) <= tolerance:
            if j >= 3:
                print("Extended std. dev: " + str(np.std(readingsI[-60:])))
                if np.std(readingsI[-60:]) <= tolerance:
                    flag = True
                    winsound.Beep(750, 750)

            
        if saveFlag == 1:    
            np.savetxt('.\\results\\Encapsulado_%s_temp\\%s\\Transitorio\\transitorio.txt' % (encapsulado, T), np.c_[time_v, readingsI])
            
        j += 1
               
    smu_2612b.write('smua.source.output = smua.OUTPUT_OFF')
    smu_2612b.write('smua.nvbuffer1.clear()')
    smu_2612b.write('smua.reset()')
    smu_2612b.close()
    
    return