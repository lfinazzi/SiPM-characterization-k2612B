from __future__ import division
#import visa
import matplotlib.pyplot as plt
import os
import numpy as np


def clear_all():
    """Clears all the variables from the workspace of the spyder application."""
    gl = globals().copy()
    for var in gl:
        if var[0] == '_': continue
        if 'func' in str(globals()[var]): continue
        if 'module' in str(globals()[var]): continue

        del globals()[var]


def gpib(address1):
    import visa
    rm = visa.ResourceManager()
    equipment_id1 = 'GPIB0::' + str(address1) + '::INSTR'
    
    smu_2612b = rm.open_resource(equipment_id1)

    print("Installed equipment:")
    print(smu_2612b.query("*IDN?"))
    
    smu_2612b.write('reset()')    
    smu_2612b.write('smua.reset()')
    smu_2612b.write('smub.reset()')
   
    return smu_2612b, rm


#could pur a flag on plot to decide what data to plot (I, V, R)
def plot(x, y, char1, char2, n, log=False, errorbars_2400=False, errorbars_2602=False, errorbars_2612=False, xflag='V'):
    graph = plt.figure(n)
    #plt.hold(True)
    
    if errorbars_2612:
        y_err = error_I(y, '2612', source=False)
        if xflag == 'V':
            x_err = error_V(x, '2612', source=True)
        elif xflag == 'I':
            x_err = error_I(x, '2612', source=True)
        elif xflag == 't':
            import numpy as np
            size =len(x)
            x_err = np.zeros(size)
        else:
            print("Not a valid flag for plot")
            
    if errorbars_2602:
        y_err = error_I(y, '2602', source=False)
        if xflag == 'V':
            x_err = error_V(x, '2602', source=True)
        elif xflag == 'I':
            x_err = error_I(x, '2602', source=True)
        else:
            print("Not a valid flag for plot")
        
        plt.errorbar(x, y, xerr=x_err, yerr=y_err, fmt='.k', capsize=3)
        
    if errorbars_2400:
        y_err = [0.0007*i + 0.3 for i in y]
        plt.errorbar(x, y, yerr=y_err, fmt='.k', capsize=3)

    else:
        plt.plot(x, y, '.', linewidth = 1.0)
        #plt.legend(loc = 'best')

    if (char1 == 'N'):
        plt.xlabel('Number of measurement', fontsize = 14)
    if (char1 == 't'):
        plt.xlabel('Time [s]', fontsize = 14)
    elif (char1 == 'V'):
        plt.xlabel('Voltage [V]', fontsize = 14)
    elif (char1 == 'I'):
        plt.xlabel('Current [A]', fontsize = 14) 
    elif (char1 == 'Vled'):
        plt.xlabel('Led Voltage [V]', fontsize = 14)
    elif (char1 == 'Iled'):
        plt.xlabel('Led Current [A]', fontsize = 14)
    elif (char1 == 'Powled'):
        plt.xlabel('Led Power [W]', fontsize = 14)
    
    if (char2 == 'R'):
        plt.ylabel('Resistance [Ohm]', fontsize = 14)
    elif (char2 == 'I'):
        plt.ylabel('Current [A]', fontsize = 14)
    elif (char2 == 'Isipm'):
        plt.ylabel('SiPM Current [A]', fontsize = 14)
        
    if log:
        plt.xscale('log')
        plt.yscale('log')
    plt.grid(True)
    plt.tight_layout(True)
    
    plt.show()
    return graph
        

def save_iv(readingsV_sipm, readingsI_sipm, graphIV, number, group_path):
    
    #[unused,unused,dateString] = date_time_now()
    # For makin this cross platform, change the path name
    path            = ".\\results\\" + group_path + "\\"
    path_fig        = ".\\results\\" + group_path + "\\figures\\"
    ext_fig         = ".png" 
    ext_txt         = ".txt" 
    figure_nameIV   = path_fig + str(number) + ext_fig
    text_name       = path + str(number) + ext_txt
    
    """
    Check if the folder exists. This is only Windows compatible (because of VISA)
    """
        
    if not(os.path.exists(path)):
        os.makedirs(path)
        
    if not(os.path.exists(path_fig)):
        os.makedirs(path_fig)
          
    File = open(text_name, 'w')
    
    readingsV_sipm_err = error_V(readingsV_sipm, '2612', source=True)
    readingsI_sipm_err = error_I(readingsI_sipm, '2612', source=False)
    
    File.write("V_sipm\tI_sipm\tV_sipm_error\tI_sipm_error\n")
    #format is I_sipm, V_led, I_led
    if len(readingsI_sipm) == len(readingsV_sipm):
        for i in range(0, len(readingsI_sipm)):
            line = str(readingsV_sipm[i]) + '\t' + str(readingsI_sipm[i]) + '\t' + str(readingsV_sipm_err[i]) + '\t' + str(readingsI_sipm_err[i]) + '\n' 
            File.write(line)
            

    File.close()
    if graphIV != 'NULL':
        graphIV.savefig(figure_nameIV, dpi=250, bbox_inches='tight')
        

def save_dark(readingsI_sipm, graphIV, number, group_path):
    
    #[unused,unused,dateString] = date_time_now()
    # For makin this cross platform, change the path name
    
    path            = ".\\results\\" + group_path + "\\"
    path_fig        = ".\\results\\" + group_path + "\\figures\\"
    ext_fig         = ".png" 
    ext_txt         = ".txt" 
    text_name       = path + str(number) + ext_txt
    figure_nameIV   = path_fig + str(number) + ext_fig
    
    """
    Check if the folder exists. This is only Windows compatible (because of VISA)
    """
        
    if not(os.path.exists(path)):
        os.makedirs(path)
        
    if not(os.path.exists(path_fig)):
        os.makedirs(path_fig)
          
    File = open(text_name, 'w')
    
    number = []
    for g in range(len(readingsI_sipm)):
        number.append(g)
        
    readingsI_sipm_err = error_I(readingsI_sipm, '2612', source=False)
    
    File.write("N\tI_sipm\tI_sipm_error\n")
    for i in range(0,len(readingsI_sipm)):
        line = str(number[i]) + '\t' + str(readingsI_sipm[i]) + '\t' + str(readingsI_sipm_err[i]) + '\n' 
        File.write(line)
            

    File.close()
    if graphIV != 'NULL':
        graphIV.savefig(figure_nameIV, dpi=250, bbox_inches='tight')
    return


def save_led(readingsI_sipm, readingsI_led, readingsV_led, graphIV, number, group_path):
    
    #[unused,unused,dateString] = date_time_now()
    # For makin this cross platform, change the path name
    path            = ".\\results\\" + group_path + "\\"
    path_fig        = ".\\results\\" + group_path + "\\figures\\"
    ext_fig         = ".png" 
    ext_txt         = ".txt" 
    figure_nameIV   = path_fig + str(number) + ext_fig
    text_name       = path + str(number) + ext_txt
    
    """
    Check if the folder exists. This is only Windows compatible (because of VISA)
    """
        
    if not(os.path.exists(path)):
        os.makedirs(path)
        
    if not(os.path.exists(path_fig)):
        os.makedirs(path_fig)
          
    File = open(text_name, 'w')
    
    # autorange for zener
    readingsI_sipm_err = error_I(readingsI_sipm, '2612', source=False)
    readingsI_led_err = error_I(readingsI_led, '2612', source=True)
    readingsV_led_err = error_V(readingsV_led, '2612', source=False)
    
    # these errors for measurement without R or zener
#    readingsI_sipm_err = [i*0.0002 + 200E-9 for i in readingsI_sipm]
#    readingsI_led_err = [i*0.0006 + 100E-12 for i in readingsI_led]
#    readingsV_led_err = [i*0.00015 + 5E-3 for i in readingsV_led]
    
    File.write("I_sipm\tI_led\tV_led\tI_sipm_error\tI_led_error\tV_led_error\n")
    #format is I_sipm, V_led, I_led
    if len(readingsI_sipm) == len(readingsI_led):
        for i in range(0, len(readingsI_sipm)):
            line = str(readingsI_sipm[i]) + '\t' + str(readingsI_led[i]) + '\t' + str(readingsV_led[i]) + '\t' + str(readingsI_sipm_err[i]) + '\t' + str(readingsI_led_err[i]) + '\t' + str(readingsV_led_err[i]) + '\n' 
            File.write(line)
            

    File.close()
    if graphIV != 'NULL':
        graphIV.savefig(figure_nameIV, dpi=250, bbox_inches='tight')


def save_delay(time_sipm, readingsI_sipm, time_led, readingsV_led, readingsI_led, graphIsipm, graphIled, number, group_path):
    
    path            = ".\\results\\" + group_path + "\\"
    path_fig        = ".\\results\\" + group_path + "\\figures\\"
    ext_fig         = ".png" 
    ext_txt         = ".txt" 
    figure_nameIV   = path_fig + str(number)
    text_name       = path + str(number) + ext_txt
    
    """
    Check if the folder exists. This is only Windows compatible (because of VISA)
    """
        
    if not(os.path.exists(path)):
        os.makedirs(path)
        
    if not(os.path.exists(path_fig)):
        os.makedirs(path_fig)
          
    File = open(text_name, 'w')
    
    readingsI_sipm_err = error_I(readingsI_sipm, '2612', source=False)
    readingsI_led_err = error_I(readingsI_led, '2612', source=True)
    readingsV_led_err = error_V(readingsV_led, '2612', source=False)
    
    File.write("time_sipm\tI_sipm\ttime_led\tI_led\tI_sipm_error\tI_led_error\tV_led\tV_led_error\n")
    #format is I_sipm, V_led, I_led
    if len(readingsI_sipm) == len(readingsI_led):
        for i in range(0, len(readingsI_sipm)):
            line = str(time_sipm[i]) + '\t' + str(readingsI_sipm[i]) + '\t' + str(time_led[i]) + '\t' + str(readingsI_led[i]) + '\t' + str(readingsI_sipm_err[i]) + '\t' + str(readingsI_led_err[i]) + '\t' + str(readingsV_led[i]) + '\t' + str(readingsV_led_err[i]) + '\n' 
            File.write(line)
            

    File.close()
    if graphIsipm != 'NULL':
        graphIsipm.savefig(figure_nameIV + str(" (SiPM)") + ext_fig, dpi=250, bbox_inches='tight')
    if graphIled != 'NULL':
        graphIled.savefig(figure_nameIV + str(" (LED)") + ext_fig, dpi=250, bbox_inches='tight')
        

def P(prefix):
    if prefix == 'p':
        return 1E-12
    if prefix == 'n':
        return 1E-09
    if prefix == 'u':
        return 1E-06    
    if prefix == 'm':
        return 1E-03
    if prefix == 'k':
        return 1E+03
    if prefix == 'M':
        return 1E+06
    if prefix == 'G':
        return 1E+09


"""----------------------------------------------------------------------------
Configuration functions for 2612B
----------------------------------------------------------------------------"""

def readBuffer(smu, char, name_buffer='nvbuffer1', source_values=True, time_stamps=False):
    try:
        measure = smu.query('printbuffer(1, smu%s.%s.n, smu%s.%s.readings)' % (char, name_buffer, char, name_buffer))
        if source_values == True and time_stamps == False:
            source = smu.query('printbuffer(1, smu%s.%s.n, smu%s.%s.sourcevalues)' % (char, name_buffer, char, name_buffer))
            
            out_measure = []
            out_source = []
            for values_measure in measure.split(','):
                aux_measure = values_measure
                out_measure.append(float(aux_measure))
            for values_source in source.split(','):
                aux_source = values_source
                out_source.append(float(aux_source))         
            
            return out_measure, out_source 
        
        elif source_values == False and time_stamps == True:
            time_stamps = smu.query('printbuffer(1, smu%s.%s.n, smu%s.%s.timestamps)' % (char, name_buffer, char, name_buffer))
            
            out_measure = []
            out_time = []
            for values_measure in measure.split(','):
                aux_measure = values_measure
                out_measure.append(float(aux_measure))
            for values_time in time_stamps.split(','):
                aux_time = values_time
                out_time.append(float(aux_time))         
            
            return out_measure, out_time 
        
        elif source_values == True and time_stamps == True:
            source = smu.query('printbuffer(1, smu%s.%s.n, smu%s.%s.sourcevalues)' % (char, name_buffer, char, name_buffer))
            time_stamps = smu.query('printbuffer(1, smu%s.%s.n, smu%s.%s.timestamps)' % (char, name_buffer, char, name_buffer))
            
            out_measure = []
            out_source = []
            out_time = []
            for values_measure in measure.split(','):
                aux_measure = values_measure
                out_measure.append(float(aux_measure))
            for values_source in source.split(','):
                aux_source = values_source
                out_source.append(float(aux_source))  
            for values_time in time_stamps.split(','):
                aux_time = values_time
                out_time.append(float(aux_time))         
            
            return out_measure, out_source, out_time
        
        out_measure = []

        for values_measure in measure.split(','):
            aux_measure = values_measure
            out_measure.append(float(aux_measure))        
        
        
        return out_measure
    except ValueError:
        print("Could not read buffer") 


#def cast(string):
#   out = []
#   for values in string.split(','):
#       aux = values
#       out.append(float(aux))
#   return out

def split(v, i):
    v_pos = []
    v_neg = []
    i_pos = []
    i_neg = []
    
    for j in range(len(v)):
        if v[j] <= 0:
            v_neg.append(v[j])
            i_neg.append(i[j])
        elif v[j] >= 0:
            v_pos.append(v[j])
            i_pos.append(i[j])
            
    v_neg = v_neg[::-1]
    v_neg = [-g for g in v_neg]
    i_neg = i_neg[::-1]
    i_neg = [-g for g in i_neg]
    
    return v_neg, v_pos, i_neg, i_pos

#def Calibration(v):
#    
#    v_mean = np.mean(v)
#    def f(x, m, b):
#        return (1/b)*np.log(x/m)
#    if v_mean < 8.56341067e-08:
#        m = 6.50680489e-07
#        b = 5.82739964e-02
#    elif v_mean >= 8.56341067e-08 and v_mean < 1.39565946e-07:
#        m = 1.04295847e-06
#        b = 7.18314079e-02
#    elif v_mean >= 1.39565946e-07 and v_mean < 2.11484958e-07:
#        m = 7.53777754e-07
#        b = 6.02342982e-02
#    elif v_mean >= 2.11484958e-07 and v_mean < 3.26180679e-07:
#        m = 7.27517113e-07
#        b = 5.85537272e-02
#    elif v_mean >= 3.26180679e-07 and v_mean < 4.79609758e-07:
#        m = 7.17488005e-07
#        b = 5.75404942e-02
#    elif v_mean >= 4.79609758e-07 and v_mean < 7.56305642e-07:
#        m = 7.25629071e-07
#        b = 5.91523133e-02
#    elif v_mean >= 7.56305642e-07 and v_mean < 1.10826083e-06:
#        m = 7.25349213e-07
#        b = 5.97033854e-02
#    elif v_mean >= 1.10826083e-06 and v_mean < 1.83257758e-06:
#        m = 6.97013791e-07
#        b = 6.53157820e-02
#    elif v_mean >= 1.83257758e-06 and v_mean < 2.66847275e-06:
#        m = 6.15830511e-07
#        b = 7.36829046e-02
#    elif v_mean >= 2.66847275e-06 and v_mean < 4.04051346e-06:
#        m = 5.28727290e-07
#        b = 8.13461711e-02
#    elif v_mean >= 4.04051346e-06 and v_mean < 6.45009733e-06:
#        m = 3.89751688e-07
#        b = 9.35446887e-02
#    elif v_mean >= 6.45009733e-06 and v_mean < 1.05866496e-05:
#        m = 3.69889841e-07
#        b = 9.52881756e-02
#    elif v_mean >= 1.05866496e-05:
#        m = 2.79219456e-07
#        b = 1.03277016e-01
#
#    return f(v_mean, m, b), 0.3 #f(1, m, b)*(1/v_mean)*np.std(v)/15


def Vbr(t):
    m = 0.02046
    b = 24.27
    return m*t + b 
          

def error_I(y, SMU, source = False):
    """
    Esta funcion esta diseniada para crear un array con los errores de la corriente 
    medida o sourceada por un Kiethley 2611B, 2612B, 2614B.
    La funcion toma una lista que tiene la corriente, y un boolean que indica si la 
    corriente fue medida o sourceada.
    
    Input: (I, source = False)
    
    Si no se especifica el source, entonc
    I_led_temp_1 = I_led[1:int(len(I_led)/2)]es la corriente fue medida. Si source = True,
    entonces se sourceo con corriente.
    
    Returns:  I_err  (list)
    .
    .
    """
    if SMU == '2612':
        I_temp= y
        temp = []
        percentage = 0
        offset = 0
        if source == True:
            for i in range(0, len(I_temp)):
                if I_temp[i] <= 100*pow(10, -9):
                    percentage = 0.0006
                    offset = 100*pow(10, -12)
                elif 100*pow(10, -9) < I_temp[i] and I_temp[i] <= 1*pow(10, -6):
                    percentage = 0.0003
                    offset = 800*pow(10, -12)    
                elif 1*pow(10, -6)<I_temp[i] and I_temp[i]<=10*pow(10, -6): 
                    percentage = 0.0003
                    offset = 5*pow(10, -9)
                elif 10*pow(10, -6)<I_temp[i] and I_temp[i]<=100*pow(10, -6): 
                    percentage = 0.0003
                    offset = 60*pow(10, -9)
                elif 100*pow(10, -6)<I_temp[i] and I_temp[i]<=1*pow(10, -3): 
                    percentage = 0.0003
                    offset = 300*pow(10, -9)
                elif 1*pow(10, -3)<I_temp[i] and I_temp[i]<=10*pow(10, -3): 
                    percentage = 0.0003
                    offset = 6*pow(10, -6)
                elif 10*pow(10, -3)<I_temp[i] and I_temp[i]<=100*pow(10, -3): 
                    percentage = 0.0003
                    offset = 30*pow(10, -6)                
                elif 100*pow(10, -3)<I_temp[i] and I_temp[i]<=1: 
                    percentage = 0.0005
                    offset = 1.8*pow(10, -3)
                elif 1<I_temp[i] and I_temp[i] <= 1.5: 
                    percentage = 0.0006
                    offset = 4*pow(10, -3)
                else:
                    percentage = 0.005
                    offset = 40*pow(10, -3)
                temp.append(I_temp[i]*percentage + offset)
                
        elif source==False:
            for i in range(0, len(I_temp)):
                if I_temp[i] <= 100*pow(10, -9):
                    percentage = 0.0006
                    offset = 100*pow(10, -12)
                elif 100*pow(10, -9) < I_temp[i] and I_temp[i] <= 1*pow(10, -6):
                    percentage = 0.00025
                    offset = 500*pow(10, -12)    
                elif 1*pow(10, -6)<I_temp[i] and I_temp[i]<=10*pow(10, -6): 
                    percentage = 0.00025
                    offset = 1.5*pow(10, -9)
                elif 10*pow(10, -6)<I_temp[i] and I_temp[i]<=100*pow(10, -6): 
                    percentage = 0.0002
                    offset = 25*pow(10, -9)
                elif 100*pow(10, -6)<I_temp[i] and I_temp[i]<=1*pow(10, -3): 
                    percentage = 0.0002
                    offset = 200*pow(10, -9)
                elif 1*pow(10, -3)<I_temp[i] and I_temp[i]<=10*pow(10, -3): 
                    percentage = 0.0002
                    offset = 2.5*pow(10, -6)
                elif 10*pow(10, -3)<I_temp[i] and I_temp[i]<=100*pow(10, -3): 
                    percentage = 0.0002
                    offset = 20*pow(10, -6)                
                elif 100*pow(10, -3)<I_temp[i] and I_temp[i]<=1: 
                    percentage = 0.0003
                    offset = 1.5*pow(10, -3)
                elif 1<I_temp[i] and I_temp[i] <=1.5: 
                    percentage = 0.0005
                    offset = 3.5*pow(10, -3)
                else:
                    percentage = 0.004
                    offset = 25*pow(10, -3)
                temp.append(I_temp[i]*percentage + offset)
        else:
            print('Boolean values True or False.')
            
            
    if SMU == '2602':
        I_temp= y
        temp = []
        percentage = 0
        offset = 0
        if source == True:
            for i in range(0, len(I_temp)):
                if I_temp[i] <= 100*pow(10, -9):
                    percentage = 0.0006
                    offset = 100*pow(10, -12)
                elif 100*pow(10, -9) < I_temp[i] and I_temp[i] <= 1*pow(10, -6):
                    percentage = 0.0003
                    offset = 800*pow(10, -12)    
                elif 1*pow(10, -6)<I_temp[i] and I_temp[i]<=10*pow(10, -6): 
                    percentage = 0.0003
                    offset = 5*pow(10, -9)
                elif 10*pow(10, -6)<I_temp[i] and I_temp[i]<=100*pow(10, -6): 
                    percentage = 0.0003
                    offset = 60*pow(10, -9)
                elif 100*pow(10, -6)<I_temp[i] and I_temp[i]<=1*pow(10, -3): 
                    percentage = 0.0003
                    offset = 300*pow(10, -9)
                elif 1*pow(10, -3)<I_temp[i] and I_temp[i]<=10*pow(10, -3): 
                    percentage = 0.0003
                    offset = 6*pow(10, -6)
                elif 10*pow(10, -3)<I_temp[i] and I_temp[i]<=100*pow(10, -3): 
                    percentage = 0.0003
                    offset = 30*pow(10, -6)                
                elif 100*pow(10, -3)<I_temp[i] and I_temp[i]<=1: 
                    percentage = 0.0005
                    offset = 1.8*pow(10, -3)
                elif 1<I_temp[i] and I_temp[i] <= 1.5: 
                    percentage = 0.0006
                    offset = 4*pow(10, -3)
                else:
                    percentage = 0.005
                    offset = 40*pow(10, -3)
                temp.append(I_temp[i]*percentage + offset)
                
        elif source==False:
            for i in range(0, len(I_temp)):
                if I_temp[i] <= 100*pow(10, -9):
                    percentage = 0.0005
                    offset = 100*pow(10, -12)
                elif 100*pow(10, -9) < I_temp[i] and I_temp[i] <= 1*pow(10, -6):
                    percentage = 0.00025
                    offset = 500*pow(10, -12)    
                elif 1*pow(10, -6)<I_temp[i] and I_temp[i]<=10*pow(10, -6): 
                    percentage = 0.00025
                    offset = 1.5*pow(10, -9)
                elif 10*pow(10, -6)<I_temp[i] and I_temp[i]<=100*pow(10, -6): 
                    percentage = 0.0002
                    offset = 25*pow(10, -9)
                elif 100*pow(10, -6)<I_temp[i] and I_temp[i]<=1*pow(10, -3): 
                    percentage = 0.0002
                    offset = 200*pow(10, -9)
                elif 1*pow(10, -3)<I_temp[i] and I_temp[i]<=10*pow(10, -3): 
                    percentage = 0.0002
                    offset = 2.5*pow(10, -6)
                elif 10*pow(10, -3)<I_temp[i] and I_temp[i]<=100*pow(10, -3): 
                    percentage = 0.0002
                    offset = 20*pow(10, -6)                
                elif 100*pow(10, -3)<I_temp[i] and I_temp[i]<=1: 
                    percentage = 0.0003
                    offset = 1.5*pow(10, -3)
                elif 1<I_temp[i] and I_temp[i] <=1.5: 
                    percentage = 0.0005
                    offset = 3.5*pow(10, -3)
                else:
                    percentage = 0.004
                    offset = 25*pow(10, -3)
                temp.append(I_temp[i]*percentage + offset)
        else:
            print('Boolean values True or False.')
    
    elif SMU == '2400':
        I_temp= y
        temp = []
        percentage = 0
        offset = 0
        if source == False:
            for i in range(0, len(I_temp)):
                if I_temp[i] <= 1*pow(10, -6):
                    percentage = 0.00029
                    offset = 300*pow(10, -12)
                elif 1*pow(10, -6) < I_temp[i] and I_temp[i] <= 10*pow(10, -6):
                    percentage = 0.00027
                    offset = 700*pow(10, -12)    
                elif 10*pow(10, -6)<I_temp[i] and I_temp[i]<=100*pow(10, -6): 
                    percentage = 0.00025
                    offset = 6*pow(10, -9)
                elif 100*pow(10, -6)<I_temp[i] and I_temp[i]<=1*pow(10, -3): 
                    percentage = 0.00027
                    offset = 60*pow(10, -9)
                elif 1*pow(10, -3)<I_temp[i] and I_temp[i]<=10*pow(10, -3): 
                    percentage = 0.00035
                    offset = 600*pow(10, -9)
                elif 10*pow(10, -3)<I_temp[i] and I_temp[i]<=100*pow(10, -3): 
                    percentage = 0.00055
                    offset = 6*pow(10, -6)
                elif 100*pow(10, -3)<I_temp[i] and I_temp[i]<=1: 
                    percentage = 0.0022
                    offset = 570*pow(10, -6)                
                temp.append(I_temp[i]*percentage + offset)
                
        elif source==True:
            for i in range(0, len(I_temp)):
                if I_temp[i] <= 1*pow(10, -6):
                    percentage = 0.00035
                    offset = 600*pow(10, -12)
                elif 1*pow(10, -6) < I_temp[i] and I_temp[i] <= 10*pow(10, -6):
                    percentage = 0.00033
                    offset = 2*pow(10, -9)    
                elif 10*pow(10, -6)<I_temp[i] and I_temp[i]<=100*pow(10, -6): 
                    percentage = 0.00031
                    offset = 20*pow(10, -9)
                elif 100*pow(10, -6)<I_temp[i] and I_temp[i]<=1*pow(10, -3): 
                    percentage = 0.00034
                    offset = 200*pow(10, -9)
                elif 1*pow(10, -3)<I_temp[i] and I_temp[i]<=10*pow(10, -3): 
                    percentage = 0.00045
                    offset = 2*pow(10, -6)
                elif 10*pow(10, -3)<I_temp[i] and I_temp[i]<=100*pow(10, -3): 
                    percentage = 0.00066
                    offset = 20*pow(10, -6)
                elif 100*pow(10, -3)<I_temp[i] and I_temp[i]<=1: 
                    percentage = 0.0027
                    offset = 900*pow(10, -6)                
                temp.append(I_temp[i]*percentage + offset)
        else:
            print('Boolean values True or False.')        
    
    return temp


def error_V(x, SMU, source = True):
    """
    Esta funcion esta diseniada para crear un array con los errores del voltaje 
    medido o sourceado por un Kiethley 2611B, 2612B, 2614B.
    La funcion toma una lista que tiene el voltaje, y un boolean que indica si el 
    mismo fue medido o sourceado.
    
    Input: (V, source = True)
    
    Si no se especifica el source, entonces el voltaje fue sourceado. Si source = False,
    entonces se midio voltaje.
    
    Returns:  V_err  (list)
    .
    .
    """
    if SMU == '2612':
        V_temp = x
        temp = []
        percentage = 0
        offset = 0
        if source == True:
            for i in range(0, len(V_temp)):
                if V_temp[i] <= 200*pow(10, -3):
                    percentage = 0.0002
                    offset = 375*pow(10, -6)
                elif 200*pow(10, -3) < V_temp[i] and V_temp[i] <= 2:
                    percentage = 0.0002
                    offset = 600*pow(10, -6)    
                elif 2<V_temp[i] and V_temp[i]<=20: 
                    percentage = 0.0002
                    offset = 5*pow(10, -3)
                else:
                    percentage = 0.0002
                    offset = 50*pow(10, -3)
                temp.append(V_temp[i]*percentage + offset)
                
        elif source==False:
            for i in range(0, len(V_temp)):
                if V_temp[i] <= 200*pow(10, -3):
                    percentage = 0.00015
                    offset = 225*pow(10, -6)
                elif 200*pow(10, -3) < V_temp[i] and V_temp[i] <= 2:
                    percentage = 0.0002
                    offset = 350*pow(10, -6)    
                elif 2<V_temp[i] and V_temp[i]<=20: 
                    percentage = 0.00015
                    offset = 5*pow(10, -3)
                else:
                    percentage = 0.00015
                    offset = 50*pow(10, -3)
                temp.append(V_temp[i]*percentage + offset)
        else:
            print('Boolean values True or False.')
            
    if SMU == '2602':
        V_temp = x
        temp = []
        percentage = 0
        offset = 0
        if source == True:
            for i in range(0, len(V_temp)):
                if V_temp[i] <= 100*pow(10, -3):
                    percentage = 0.0002
                    offset = 250*pow(10, -6)
                elif 100*pow(10, -3) < V_temp[i] and V_temp[i] <= 1:
                    percentage = 0.0002
                    offset = 400*pow(10, -6)    
                elif 1<V_temp[i] and V_temp[i]<=6: 
                    percentage = 0.0002
                    offset = 1.8*pow(10, -3)
                else:
                    percentage = 0.0002
                    offset = 12*pow(10, -3)
                temp.append(V_temp[i]*percentage + offset)
                
        elif source==False:
            for i in range(0, len(V_temp)):
                if V_temp[i] <= 100*pow(10, -3):
                    percentage = 0.00015
                    offset = 150*pow(10, -6)
                elif 100*pow(10, -3) < V_temp[i] and V_temp[i] <= 1:
                    percentage = 0.00015
                    offset = 200*pow(10, -6)    
                elif 1<V_temp[i] and V_temp[i]<=6: 
                    percentage = 0.00015
                    offset = 1*pow(10, -3)
                else:
                    percentage = 0.00015
                    offset = 8*pow(10, -3)
                temp.append(V_temp[i]*percentage + offset)
        else:
            print('Boolean values True or False.')
    
    elif SMU == '2400':
        V_temp = x
        temp = []
        percentage = 0
        offset = 0
        if source == True:
            for i in range(0, len(V_temp)):
                if V_temp[i] <= 200*pow(10, -3):
                    percentage = 0.0002
                    offset = 600*pow(10, -6)
                elif 200*pow(10, -3) < V_temp[i] and V_temp[i] <= 2:
                    percentage = 0.0002
                    offset = 600*pow(10, -6)    
                elif 2<V_temp[i] and V_temp[i]<=20: 
                    percentage = 0.0002
                    offset = 2.4*pow(10, -3)
                else:
                    percentage = 0.0002
                    offset = 24*pow(10, -3)
                temp.append(V_temp[i]*percentage + offset)
                
        elif source==False:
            for i in range(0, len(V_temp)):
                if V_temp[i] <= 200*pow(10, -3):
                    percentage = 0.00012
                    offset = 300*pow(10, -6)
                elif 200*pow(10, -3) < V_temp[i] and V_temp[i] <= 2:
                    percentage = 0.00012
                    offset = 300*pow(10, -6)    
                elif 2<V_temp[i] and V_temp[i]<=20: 
                    percentage = 0.00015
                    offset = 1.5*pow(10, -3)
                else:
                    percentage = 0.00015
                    offset = 10*pow(10, -3)
                temp.append(V_temp[i]*percentage + offset)
        else:
            print('Boolean values True or False.')
        
    return temp

def DetectFolders(path):
    j = 1
    import os
    while(True):
        if os.path.exists(path + '%s' % j):
            j += 1
        else:
            break
            
    return j - 1

def weightedMean(measurements, weights):
    """
    Devuelve el promedio pesado de una muestra con sus respectivos errores.
    
    Input: (X, X_err)  lists
    
    Returns: float
    .
    .
    """
    wTotal = np.sum([1/i**2 for i in weights])
    mwTotal = 0
    mean = 0 
    
#    for i in range(0, len(weights)):
#        wTotal += (1 / weights[i]**2)
    for i in range(0, len(measurements)):
        mwTotal += measurements[i]*(1/weights[i]**2)
    mean = mwTotal / wTotal 
    
    return mean

def weightedError(measurements, weights):
    """
    A chequear
    """
    wTotal = 0
    red_chi_sq = 0
    mean = weightedMean(measurements, weights)
    
    weights = np.asarray(weights)
    for i in range(0, len(weights)):
        wTotal += 1 / weights[i]**2
        red_chi_sq += ((measurements[i] - mean)/(1/weights[i]))**2
    
    return np.sqrt(1/wTotal)#*red_chi_sq/(len(measurements) - 1)

def Linear(M, x):
    m, b = M
    return m*x + b
    
    
def ClosestToOne(v):
    compliance = []
    for j in range(0, len(v)):
        compliance.append(abs(v[j] - 1))
    return compliance.index(np.min(compliance))


def LogData(x, y, y_err):
    v = []
    for i in range(len(y)):
        try:
            v.append(np.log(y[i]))
            
        except ValueError:
            continue
        
    v_err = []
    for i in range(0, len(y)):
        v_err.append(y_err[i]/y[i])
    return x, v, v_err

def DiffData(x, y, x_err, y_err):
    h = x[1] - x[0]
    diff = []
    diff_err = []
    for i in range(1, len(y) - 1):
        diff.append((y[i - 1] - y[i + 1])/(2*h))
        diff_err.append(np.sqrt((abs(y_err[i - 1])**2 + abs(y_err[i + 1])**2))/(2*h))
        
    index = [0, len(x) - 1]    
        
    x = np.delete(x, index)
    x_err = np.delete(x_err, index)
    
    return x, diff, x_err, diff_err

def fit_function(M, x):
    b = M
    return 2.0/(x - b)


#def fit_calc(beta, sd_beta, value, perfect = False):
#    temp = []
#    temp2 = []
#    temp3 = []
#    for i in range(0, len(beta)):
#        if perfect:
#            temp.append(beta[i][0])
#            temp2.append(beta[i][1])
#            temp3.append(sd_beta[i][1])
#        else:
#            if beta[i][0] != value:
#                temp.append(beta[i][0])
#                temp2.append(beta[i][1])
#                temp3.append(sd_beta[i][1])
#    for i in range(0, len(temp)):
#        if perfect:
#            if temp[i] == value:
#                return value
#            
#        else:
#            temp = [x/value for x in temp]
#            i = ClosestToOne(temp)
#            beta_temp = [beta[k][0] for k in range(len(beta))]
#            j = beta_temp.index(value * temp[i])
#            return j, temp2[i], temp3[i]
    
def FIT(x_data, y_data, x_sigma, y_sigma):
    import numpy                  # numpy.scipy.org/
    import scipy                  # scipy.org/
    import scipy.odr, scipy.special, scipy.stats


    def Fit_Vbr(p,x) :
        return p[1]/(x - p[0])

    func = Fit_Vbr
    p_guess = (23, 1.7)
    
    # Load data for ODR fit
    data = scipy.odr.RealData(x=x_data, y=y_data, sx=x_sigma, sy=y_sigma)
    # Load model for ODR fit
    model = scipy.odr.Model(func)
    
    ## Now fit model to data
    #	job=10 selects central finite differences instead of forward
    #       differences when doing numerical differentiation of function
    #	maxit is maximum number of iterations
    #   The scipy.odr documentation is a bit murky, so to be clear note
    #        that calling ODR automatically sets full_output=1 in the
    #        low level odr function.
    fitted = scipy.odr.ODR(data, model, beta0=p_guess, maxit=500000,job=10)
    
    output = fitted.run()
    p   = output.beta      # 'beta' is an array of the parameter estimates
    #"Quasi-chi-squared" is defined to be the
    #           [total weighted sum of squares]/dof
    #	i.e. same as numpy.sum((residual/sigma_odr)**2)/dof or
    #       numpy.sum(((output.xplus-x)/x_sigma)**2
    #                                +((y_data-output.y)/y_sigma)**2)/dof
    #	Converges to conventional chi-square for zero x uncertainties.
    quasi_chisq = output.res_var
    uncertainty = output.sd_beta # parameter standard uncertainties
    #  scipy.odr scales the parameter uncertainties by quasi_chisq.
    #    If the fit is poor, i.e. quasi_chisq is large, the uncertainties
    #    are scaled up, which makes sense. If the fit is too good,
    #    i.e. quasi_chisq << 1, it suggests that the uncertainties have
    #    been overestimated, but it seems risky to scale down the
    #    uncertainties. i.e. The uncertainties shouldn't be too sensistive
    #    to random fluctuations of the data, and if the uncertainties are
    #    overestimated, this should be understood and corrected
    if quasi_chisq < 1.0 :
        uncertainty = uncertainty/numpy.sqrt(quasi_chisq)
        
    pval = 1 - scipy.stats.chi2.cdf(len(x_data)*quasi_chisq, len(x_data))
        
    return p, uncertainty, quasi_chisq, pval
    

def SmoothData(v, w, dv, dw, value_tolerance, derivative_tolerance):
    
    v2 = []
    w2 = []
    dv2 = []
    dw2 = []

    
    step = v[1] - v[0]
    derivative = []
    difference = []
    for i in range(0, len(v) - 1):
        value = w[i + 1] - w[i]
        derivative.append(value/step)
        difference.append(value)
        
        
    derivative.append(value/step)
    difference.append(value)
    
    for i in range(1, len(v) - 1):
        if abs(derivative[i] - derivative[i + 1]) < derivative_tolerance and abs(difference[i] - difference[i + 1]) < value_tolerance and abs(derivative[i - 1] - derivative[i]) < derivative_tolerance and abs(difference[i - 1] - difference[i]) < value_tolerance:
                v2.append(v[i])
                w2.append(w[i])
                dv2.append(dv[i])
                dw2.append(dw[i])
                
                
    return v2, w2, dv2, dw2

def CalibrateSMU(v, v_err):
    for i in range(0, len(v)):
        if v[i] < 1E-7:
            v[i] *= 10
            v_err[i] *= 10
            
    return v, v_err
        
        











