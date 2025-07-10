from functions import readBuffer, P
import time

def IVComplete(smu_2612b, config, breakdown):
    
    """
    
    
    
    ---------
    
    """
    
    [i_cc_sipm,
    v_cc_sipm,
    i_rang_sipm,
    v_rang_sipm,
    v_level_sipm,
    i_cc_led,
    v_cc_led,
    i_rang_led,
    v_rang_led,
    _,
    N,
    points,
    delay,
    _] = config
     

    # level with 9.7k resistor in parallel is approx. 200E-6, without R or zener
    # is approx. 200*P('n') and with zener in parallel is approx. 3E-3
    
    # 3.5 mA for low temperatures (with zener)
    i_led_level = 3.5*P('m')
    
    NPLC = 25
    
    smu_2612b.write('reset()')
    smu_2612b.write('smua.reset()')
    smu_2612b.write('smub.reset()')
    smu_2612b.write('errorqueue.clear()')
    
    
    smu_2612b.write('format.data = format.ASCII')
    

    # Buffer operations -------------------------------------------------------
    
    smu_2612b.write('smua.nvbuffer1.clear()')
    smu_2612b.write('smub.nvbuffer1.clear()')
    
    smu_2612b.write('smua.nvbuffer1.appendmode = 1')
    
    # could try to measure 50 points instead of 100 in Vbr measurement
    smu_2612b.write('smua.nvbuffer1.fillcount = ' + str(2*N))  
    
    smu_2612b.write('smua.nvbuffer1.collectsourcevalues = 1')

    smu_2612b.write('smua.measure.count = 1')
    
    smu_2612b.write('smua.nvbuffer1.clear()')
    smu_2612b.write('smub.nvbuffer1.clear()')
    

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
    
    # -------------------------------------------------------------------------   
    # smua configuration (SiPM)
    
    smu_2612b.write('smub.source.func = smub.OUTPUT_DCAMPS')
    smu_2612b.write('display.smub.measure.func = display.MEASURE_DCVOLTS')
    
    if (i_rang_led == 'AUTO'):
        smu_2612b.write('smub.source.autorangei = smub.AUTORANGE_ON')
    else:
        smu_2612b.write('smub.source.rangei = ' + str(i_rang_led))
    
    if (v_rang_led == 'AUTO'):
        smu_2612b.write('smub.measure.autorangev = smub.AUTORANGE_ON')
    else:
        smu_2612b.write('smub.measure.rangev = ' + str(v_rang_led))

    #compliance values for I and V
    smu_2612b.write('smub.source.limiti = ' + str(i_cc_led))
    smu_2612b.write('smub.source.limitv = ' + str(v_cc_led))
    
    smu_2612b.write('smub.source.leveli = ' + str(i_led_level))  
    
    v_initial = breakdown - 0.5
    v_end = breakdown + 2
        
    import numpy as np
    
    # allowed voltage values in sweep, try 50 instead of 100 in Vbr sweep
    b1 = np.arange(0, N, 1)
    b2 = np.arange(0, N, 1)
    v_sipm_values1 = [v_initial + (v_end - v_initial)/(N)*i for i in b1]
    v_sipm_values2 = [-1 + (0.5)/(N)*i for i in b2]
   
    v_sipm_values = np.concatenate((v_sipm_values1, v_sipm_values2))

    smu_2612b.write('smua.source.output = smua.OUTPUT_ON')
    smu_2612b.write('smub.source.output = smub.OUTPUT_ON') 
    
    print("Start of SiPM IV measurement\n")

    flag = False

    for j in range(len(v_sipm_values)):
        
        smu_2612b.write('smua.source.levelv = ' + str(v_sipm_values[j]))
        smu_2612b.write('smua.measure.i(smua.nvbuffer1)')
        
        time.sleep(delay + NPLC/50.0)
        
        if j != len(v_sipm_values) - 1 and flag == False:
            if v_sipm_values[j + 1] < 0:
                    smu_2612b.write('smub.source.leveli = ' + str(0))
                    smu_2612b.write('smub.source.output = smub.OUTPUT_OFF')
                	
                    smu_2612b.write('smua.measure.nplc = 1')
                    NPLC = 2

                    flag = True
                    #time.sleep(30)
        
    smu_2612b.write('smua.source.output = smua.OUTPUT_OFF')
    
    print("End of SiPM IV measurement\n")
    
    time.sleep(6)
    
    readingsI_sipm, readingsV_sipm = readBuffer(smu_2612b, 'a')

    return [readingsV_sipm, readingsI_sipm]
        

def DarkCurrent(smu_2612b, config, v_bias):
    
        
    """
    
    
    
    ---------
    
    """
    
    [i_cc_sipm,
    v_cc_sipm,
    i_rang_sipm,
    v_rang_sipm,
    v_level_sipm,
    i_cc_led,
    v_cc_led,
    i_rang_led,
    v_rang_led,
    _,
    N,
    _,
    delay,
    _] = config
     
    NPLC = 25
    
    smu_2612b.write('reset()')
    smu_2612b.write('smua.reset()')
    smu_2612b.write('smub.reset()')    
    smu_2612b.write('errorqueue.clear()')
    
    smu_2612b.write('format.data = format.ASCII')
    
    # Buffer operations -------------------------------------------------------
    
    smu_2612b.write('smua.nvbuffer1.clear()')
    smu_2612b.write('smub.nvbuffer1.clear()')
    
    smu_2612b.write('smua.nvbuffer1.appendmode = 1')
    
    smu_2612b.write('smua.nvbuffer1.fillcount = 125')
    
    smu_2612b.write('smua.nvbuffer1.collectsourcevalues = 1')

    smu_2612b.write('smua.measure.count = 125')
    
    smu_2612b.write('smua.nvbuffer1.clear()')
    smu_2612b.write('smub.nvbuffer1.clear()')

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
    
    smu_2612b.write('smua.source.levelv = ' + str(v_bias))
    
    smu_2612b.write('smua.measure.delay = ' + str(delay))
        
    # -------------------------------------------------------------------------
    
    smu_2612b.write('smua.source.output = smua.OUTPUT_ON') 


    print("Start of dark current measurement\n")
    
    smu_2612b.write('smua.measure.i(smua.nvbuffer1)')
    time.sleep(125*(delay + NPLC/50.0))
        
    smu_2612b.write('smua.source.output = smua.OUTPUT_OFF')
    
    print("End of dark current measurement\n")
    
    time.sleep(4)
    
    readingsI_sipm = readBuffer(smu_2612b, 'a', source_values=False)

    return readingsI_sipm

    
def LEDTest(smu_2612b, config, v_bias):
        
    """
    
    
    
    ---------
    
    """
    
    [i_cc_sipm,
    v_cc_sipm,
    i_rang_sipm,
    v_rang_sipm,
    v_level_sipm,
    i_cc_led,
    v_cc_led,
    i_rang_led,
    v_rang_led,
    return_sweep,
    N,
    points,
    delay,
    _] = config
     
    #current bounds with 9.7k resistor in parallel ----------------------------
    
#    iStart = 100*P('u')
#    iEnd = 219*P('u')
    
#    import numpy as np
#    
#    b3 = np.arange(0, N, 1)
#    i_led_values1 = [iStart + (iEnd - iStart)/N*i for i in b3]
#    
#    if return_sweep == 1:
#        i_led_values2 = np.flip(i_led_values1, 0)
#        i_led_values = np.concatenate((i_led_values1, i_led_values2))
#    else:
#        i_led_values = i_led_values1
    
     #-------------------------------------------------------------------------

   
     #current bounds without resistor in parallel -----------------------------
    
#    i_rang_sipm    = 1*P('m')
#    i_rang_led     = 100*P('n')
#    v_rang_led     = 20 #6 for k2602B in CAC
#    
#    import numpy as np
#    
#    iStart = 0*P('n')   
#    iStep = 100*P('p')
#        
#    b1 = np.arange(0, 30, 1)
#    b2 = np.arange(0, N - 30, 1)
#    i_led_values1 = [iStart + (iStep)*i for i in b1]
#    i_led_values2 = [3*P('n') + 1*P('n')*i for i in b2]
#   
#    i_led_values3 = np.concatenate((i_led_values1, i_led_values2))
#    
#        
#    if return_sweep == 1:
#        i_led_values4 = np.flip(i_led_values3, 0)
#        i_led_values = np.concatenate((i_led_values3, i_led_values4))
#    else:
#        i_led_values = i_led_values3
    
    # -------------------------------------------------------------------------
    
    
    # level with zener in parallel --------------------------------------------
    
#    i_rang_sipm    = 1*P('m')
#    i_rang_led     = 10*P('m')
#    v_rang_led     = 6 #6 for k2602B in CAC
    
    import numpy as np
    
    iStart = 0
    iEnd = 3.5*P('m')
    
    #iEnd = 300*P('n')
    
    b3 = np.arange(0, N, 1)
    i_led_values1 = [iStart + (iEnd - iStart)/N*i for i in b3]
    
    if return_sweep == 1:
        i_led_values2 = np.flip(i_led_values1, 0)
        i_led_values = np.concatenate((i_led_values1, i_led_values2))
    else:
        i_led_values = i_led_values1
    
    
    # -------------------------------------------------------------------------
    
    NPLC = round(points*200*P('u')*50, 2)
    
    smu_2612b.write('reset()')
    smu_2612b.write('smua.reset()')
    smu_2612b.write('smub.reset()')
    smu_2612b.write('errorqueue.clear()')
    
    smu_2612b.write('format.data = format.ASCII')
    
    # Buffer operations -------------------------------------------------------
    
    smu_2612b.write('smua.nvbuffer1.clear()')
    smu_2612b.write('smub.nvbuffer1.clear()')
    
    smu_2612b.write('smua.nvbuffer1.appendmode = 1')
    smu_2612b.write('smub.nvbuffer1.appendmode = 1')
    
    smu_2612b.write('smua.nvbuffer1.collectsourcevalues = 1')
    smu_2612b.write('smub.nvbuffer1.collectsourcevalues = 1')

    smu_2612b.write('smua.nvbuffer1.fillcount = ' + str(2*N))
    smu_2612b.write('smub.nvbuffer1.fillcount = ' + str(2*N))

    smu_2612b.write('smua.measure.count = 1')
    smu_2612b.write('smub.measure.count = 1')
            
    smu_2612b.write('smua.nvbuffer1.clear()')
    smu_2612b.write('smub.nvbuffer1.clear()')
    

    # -------------------------------------------------------------------------   
    # smua configuration (SiPM)
    
    smu_2612b.write('smua.source.func = smua.OUTPUT_DCVOLTS')
    smu_2612b.write('display.smua.measure.func = display.MEASURE_DCAMPS')
    
    if (i_rang_sipm == 'AUTO'):
        smu_2612b.write('smua.measure.autorangei = smua.AUTORANGE_ON')
    else:
        smu_2612b.write('smua.measure.rangei = ' + str(i_rang_sipm))
    
    if (v_rang_sipm == 'AUTO'):
        smu_2612b.write('smua.source.autorangev = smua.AUTORANGE_ON')
    else:
        smu_2612b.write('smua.source.rangev = ' + str(v_rang_sipm))

    #compliance values for I and V
    smu_2612b.write('smua.source.limiti = ' + str(i_cc_sipm))
    smu_2612b.write('smua.source.limitv = ' + str(v_cc_sipm))
	
    smu_2612b.write('smua.measure.nplc = ' + str(NPLC))
    
    smu_2612b.write('smua.source.levelv = ' + str(v_bias))
    
    # -------------------------------------------------------------------------   
    # smub configuration (LED)
    
    smu_2612b.write('smub.source.func = smub.OUTPUT_DCAMPS')
    smu_2612b.write('display.smub.measure.func = display.MEASURE_DCVOLTS')
    
    if (i_rang_led == 'AUTO'):
        smu_2612b.write('smub.source.autorangei = smub.AUTORANGE_ON')
    else:
        smu_2612b.write('smub.source.rangei = ' + str(i_rang_led))
    
    if (v_rang_led == 'AUTO'):
        smu_2612b.write('smub.measure.autorangev = smub.AUTORANGE_ON')
    else:
        smu_2612b.write('smub.measure.rangev = ' + str(v_rang_led))

    #compliance values for I and V
    smu_2612b.write('smub.source.limiti = ' + str(i_cc_led))
    smu_2612b.write('smub.source.limitv = ' + str(v_cc_led))
    
    smu_2612b.write('smub.measure.nplc = ' + str(NPLC))
    
    smu_2612b.write('smub.measure.delay = ' + str(delay))


    smu_2612b.write('smua.source.output = smua.OUTPUT_ON')
    smu_2612b.write('smub.source.output = smub.OUTPUT_ON')
    
    print("Start of LED measurement\n")
    

    for j in range(len(i_led_values)):
        
        smu_2612b.write('smub.source.leveli = ' + str(i_led_values[j]))
        
        smu_2612b.write('smua.measure.i(smua.nvbuffer1)')
        smu_2612b.write('smub.measure.v(smub.nvbuffer1)')
        time.sleep(2*(delay + NPLC/50.0))
                
    #smu_2612b.write('waitcomplete()') 
    
        
    smu_2612b.write('smua.source.output = smua.OUTPUT_OFF')
    smu_2612b.write('smub.source.output = smub.OUTPUT_OFF')
    
    time.sleep(2)
    print("End of LED measurement\n")

    
    readingsI_sipm = readBuffer(smu_2612b, 'a', source_values=False)
    readingsV_led, readingsI_led = readBuffer(smu_2612b, 'b')

    return [readingsI_sipm, readingsI_led, readingsV_led]


def SiPMDelay(smu_2612b, config, encapsulado, n, bias=30.0):
        
    """
    
    
    
    ---------
    
    """
    
    [i_cc_sipm,
    v_cc_sipm,
    i_rang_sipm,
    v_rang_sipm,
    v_level_sipm,
    i_cc_led,
    v_cc_led,
    i_rang_led,
    v_rang_led,
    _,
    N,
    points,
    _,
    _] = config
     
   
    # WITH9.7K R IN PARALLEL --------------------------------------------------
    
#    allowed_currents = [200*P('u'), 202.5*P('u'), 205*P('u'), 207.5*P('u'), 210*P('u'), 212.5*P('u'), 215*P('u')]
#    allowed_currents = [200*P('u'), 201*P('u'), 202*P('u'), 203*P('u'), 204*P('u'), 205*P('u'), 206*P('u'), 207*P('u'), 208*P('u'), 209*P('u'), 210*P('u'), 211*P('u'), 212*P('u'), 213*P('u'), 214*P('u'), 215*P('u'), 216*P('u'), 217*P('u'), 218*P('u')]

    # -------------------------------------------------------------------------
    

    # WITHOUT R OR ZENER IN PARALLEL ------------------------------------------
    
#    allowed_currents = [1E-1, 7, 12, 18, 27, 39, 54, 65, 75, 83]
    
#    allowed_currents = [1, 30, 60, 90, 120, 150, 180, 210, 235, 260]
#    allowed_currents = [i*1E-9 for i in allowed_currents]
    
    # -------------------------------------------------------------------------
    
    
    # FOR ZENER IN PARALLEL --------------------------------------------------
    
    iStart = 1*P('m')
    iEnd = 3.5*P('m')
    
    import numpy as np
    b = np.arange(0, 5, 1)
    allowed_currents = [iStart + (iEnd - iStart)/4*i for i in b]
     
    # ------------------------------------------------------------------------
    
    
    NPLC = 25.0
    
    smu_2612b.write('reset()')
    smu_2612b.write('smua.reset()')
    smu_2612b.write('smub.reset()')
    smu_2612b.write('errorqueue.clear()')
    
    smu_2612b.write('format.data = format.ASCII')
    
    # Buffer operations -------------------------------------------------------
    
    smu_2612b.write('smua.nvbuffer1.clear()')
    smu_2612b.write('smub.nvbuffer1.clear()')
    
    smu_2612b.write('smua.nvbuffer1.appendmode = 1')
    smu_2612b.write('smub.nvbuffer1.appendmode = 1')
    
    smu_2612b.write('smua.nvbuffer1.collectsourcevalues = 1')
    smu_2612b.write('smub.nvbuffer1.collectsourcevalues = 1')
    
    smu_2612b.write('smua.nvbuffer1.collecttimestamps = 1')
    smu_2612b.write('smub.nvbuffer1.collecttimestamps = 1')
    
    smu_2612b.write('smua.nvbuffer1.fillcount = ' + str(100*N))
    smu_2612b.write('smub.nvbuffer1.fillcount = ' + str(100*N))

    smu_2612b.write('smua.measure.count = 1')
    smu_2612b.write('smub.measure.count = 1')
            
    smu_2612b.write('smua.nvbuffer1.clear()')
    smu_2612b.write('smub.nvbuffer1.clear()')
    

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
    
    smu_2612b.write('smua.source.levelv = ' + str(bias))
    
    smu_2612b.write('smua.measure.delay = 0')
    
    # -------------------------------------------------------------------------   
    # smub configuration (LED)
    
    smu_2612b.write('smub.source.func = smub.OUTPUT_DCAMPS')
    smu_2612b.write('display.smub.measure.func = display.MEASURE_DCVOLTS')
    
    if (i_rang_led == 'AUTO'):
        smu_2612b.write('smub.source.autorangei = smub.AUTORANGE_ON')
    else:
        smu_2612b.write('smub.source.rangei = ' + str(i_rang_led))
    
    if (v_rang_led == 'AUTO'):
        smu_2612b.write('smub.measure.autorangev = smub.AUTORANGE_ON')
    else:
        smu_2612b.write('smub.measure.rangev = ' + str(v_rang_led))

    #compliance values for I and V
    smu_2612b.write('smub.source.limiti = ' + str(i_cc_led))
    smu_2612b.write('smub.source.limitv = ' + str(v_cc_led))
    
    smu_2612b.write('smub.measure.nplc = ' + str(NPLC))
    
    smu_2612b.write('smub.measure.delay = 0')    

    smu_2612b.write('smua.source.output = smua.OUTPUT_ON')
    smu_2612b.write('smub.source.output = smub.OUTPUT_ON')

    
    for j in range(0, len(allowed_currents)):
        smu_2612b.write('smub.source.leveli = ' + str(allowed_currents[j]))
        
        #while time.time() - startTime < 10:
        for i in range(0, 40):
            
#            if time.time() - startTime > 90:
#                smu_2612b.write('smub.source.leveli = 0')
            
#            for i in range(0, int(N)):
            smu_2612b.write('smua.measure.i(smua.nvbuffer1)')
            time.sleep(NPLC/50.0)
            smu_2612b.write('smub.measure.v(smub.nvbuffer1)')
            time.sleep(NPLC/50.0)   
            
        smu_2612b.write('smub.source.leveli = 0')      
        for i in range(0, 100):
            smu_2612b.write('smua.measure.i(smua.nvbuffer1)')
            smu_2612b.write('smub.measure.v(smub.nvbuffer1)')
    
    smu_2612b.write('smua.source.output = smua.OUTPUT_OFF')
    smu_2612b.write('smub.source.output = smub.OUTPUT_OFF')
    
    print("End of measurement")
    import winsound
    winsound.Beep(750, 750)
    time.sleep(60)
    
    readingsI_sipm, time_sipm = readBuffer(smu_2612b, 'a', source_values=False, time_stamps=True)
    readingsV_led, readingsI_led, time_led = readBuffer(smu_2612b, 'b', source_values=True, time_stamps=True)


    from functions import plot, save_delay
    
    path = "/Encapsulado_%s_delay/" % encapsulado
    
    graph_sipm = plot(time_sipm, readingsI_sipm, 't', 'Isipm', 1, errorbars_2612=True, xflag='t', log=True)    
    graph_led = plot(time_led, readingsV_led, 't', 'Vled', 2, errorbars_2612=True, xflag='t')

    
    save_delay(time_sipm, readingsI_sipm, time_led, readingsV_led, readingsI_led, graph_sipm, graph_led, n, path)

    return time_sipm, readingsI_sipm, time_led, readingsV_led, readingsI_led  
    
