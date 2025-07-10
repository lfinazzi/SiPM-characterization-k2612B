from __future__ import division
import os
import time
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as sp

#current working directory (all paths relative to this one)
#home_path = "C:/Users/lucas/Desktop/LabOSat CAC/"
home_path = "C:/Users/LINE/Desktop/LabOSat CAC/"
os.chdir(home_path)

from functions import DetectFolders

from functions import weightedMean, weightedError, error_V, error_I, Linear, ClosestToOne, LogData, DiffData, fit_function
from functions import FIT, SmoothData, CalibrateSMU
from scipy.odr import ODR, Model, RealData
from scipy.signal import savgol_filter
import scipy.stats

#constants for data analysis

pixels = 18980

#number of package
encapsulado = 3

#number of try (or measurement set) for said package
enc_try = 2

keithley = '2612'


folders = DetectFolders("results/Encapsulado_%s/sd_test_%s/" % (str(encapsulado), str(enc_try)))

os.chdir("results/Encapsulado_%s/sd_test_%s/" % (str(encapsulado), str(enc_try)))


def CalculateRqT():
    
    Rq = []    
    Rq_err = []
    
    path_R = 'temperatures.txt'
    T = np.loadtxt(path_R, skiprows=1)[:, 5]
    T_err = np.loadtxt(path_R, skiprows=1)[:, 6] 
    
    
    for i in range(1, folders + 1):
    
        path = '%s/rq' % i
    
        Rq_temp = []
        Rq_err_temp = []
    
        for j in range(1, 6):
            
            path_group = '/%s.txt' % j
            data_vbr = np.loadtxt(path + path_group, skiprows=1)
            V = data_vbr[:, 0]
            I = data_vbr[:, 1]
            V_err = error_V(V, keithley)
            I_err = error_I(I, keithley)
                
            chi_2 = []
            beta = []
            sd_beta = []
            
            for h in range(0, len(V) - 10):
                V_fit = V[h:]
                I_fit = I[h:]
                I_err_fit = I_err[h:]
                V_err_fit = V_err[h:]
                model = Model(Linear)
                data = RealData(V_fit, I_fit, sx=V_err_fit, sy=I_err_fit)
                odr = ODR(data, model, beta0=[0., 0.03], maxit=10000000)
                out = odr.run()
                
                beta.append(out.beta[0])
                sd_beta.append(out.sd_beta[0])
                chi_2.append(out.res_var)
    
    
          
            index = ClosestToOne(chi_2)
            Rq_temp.append(pixels/beta[index])
            Rq_err_temp.append(pixels/(beta[index]**2)*sd_beta[index])
            print("%s/%s" % (j, 6))
            
        Rq.append(weightedMean(Rq_temp, Rq_err_temp))
        Rq_err.append(weightedError(Rq_temp, Rq_err_temp))
        print("success!: "+ str(i))
            
    plt.errorbar(T, Rq, xerr=T_err, yerr=Rq_err, fmt='.k', capsize=3)
    plt.grid(True)
    plt.xlabel('Temperature [C]')
    plt.ylabel('Quenching Resistance [Ohm]')
    plt.tight_layout(True)
    
    return

def CalculateVbrT_fit():

    start = time.time()
    
    path_R = 'temperatures.txt'
    T = np.loadtxt(path_R, skiprows=1)[:, 5]
    T_err = np.loadtxt(path_R, skiprows=1)[:, 6]
    
    Vbr = []
    Vbr_err = []
    T_lista = []
    T_err_lista = []
    Vbr_lista = []
    Vbr_err_lista = []
    
    chi = []
    pvalue = []
    
    for i in range(1, folders + 1):
    
        path = '%s/vbr' % i
        Vbr_temp = []
        Vbr_err_temp = []
        T_temp = []
        T_err_temp_lista = []
#        breakdown_fit = 24.3 + T[i - 1]*0.0215
        
#        V = []
#        I = []
#        V_err = []
#        I_err = []
#        for j in range(0, 100):
#            V.append([])
#            I.append([])
#            V_err.append([])
#            I_err.append([])
    
        for j in range(1, 6):
            path_group = '/%s.txt' % j
            data_vbr = np.loadtxt(path + path_group, skiprows=1)
            V = data_vbr[:, 0]
            I = data_vbr[:, 1]
            V_err = error_V(V, keithley)
            I_err = error_I(I, keithley)
        
            V, I, I_err = LogData(V, I, I_err)
            V, I, V_err, I_err = DiffData(V, I, V_err, I_err)
            
            I = I[10:]
            V = V[10:]
            I_err = I_err[10:]
            V_err = V_err[10:]
            
            V, I, V_err, I_err = SmoothData(V, I, V_err, I_err, 1, 20)
            
            #y = savgol_filter(I, 9, 3)
            
            #I = np.asarray(y)
    
            #flag to check if data needs to be inverted
            
#            if abs(np.max(I)) > abs(np.min(I)):
#                index = I.index(np.max(I))
#            elif abs(np.max(I)) < abs(np.min(I)):
#                index = I.index(np.min(I))
#                I = [-x for x in I]
            
            if abs(np.max(I)) > abs(np.min(I)):
                index = np.where(I == np.max(I))[0][0]
            elif abs(np.max(I)) < abs(np.min(I)):
                index = np.where(I == np.min(I))[0][0]
                I = [-x for x in I]
                
            
            #plt.errorbar(V, I, xerr=V_err, yerr=I_err, fmt='.')
                
#            chi_2 = []
#            pval = []
#            beta = []
#            sd_beta = []
            
#            for l in range(0, 5):
#                for h in range(l, len(V[index:]) - 20):
#                    V_fit = V[index + l:index + h]
#                    I_fit = I[index + l:index + h]
#                    I_err_fit = I_err[index + l:index + h]
#                    V_err_fit = V_err[index + l:index + h]
#                    model = Model(fit_function)
#                    data = RealData(V_fit, I_fit, sx=V_err_fit, sy=I_err_fit)
#                    odr = ODR(data, model, beta0=[breakdown_fit], maxit=10000000, job=10)
#                    #odr = ODR(data, model, beta0=[2.0, 24.], maxit=10000000)
#                    out = odr.run()
#                    
#                    if not np.isnan(out.beta[0]):
#                        beta.append(out.beta)
#                        sd_beta.append(out.sd_beta)
#                        chi_2.append(out.res_var)
#                        pval.append(1 - sp.chi2.cdf(len(V_fit)*out.res_var, len(V_fit)))
                        
                    #print(h)
    
#            index_chi = ClosestToOne(chi_2)
                    
            o = 2
            f = 40 #len(V[index:]) - 1
            p, dp, chi2, pval = FIT(V[index + o:index + f], I[index + o:index + f], V_err[index + o:index + f], I_err[index + o:index + f])
            
#            if chi_2[index_chi] > 0 and chi_2[index_chi] < 5 and pval[index_chi] <= 0.95 and pval[index_chi] >= 0.25:
#                Vbr_temp.append(beta[index_chi][0])
#                T_temp.append(T[i - 1])
#                T_err_temp_lista.append(T_err[i - 1])
#                chi.append(chi_2[index_chi])
#                pvalue.append(pval[index_chi])
#                
#                if chi_2[index_chi] < 1.0 :
#                    uncertainty = sd_beta[index_chi][0]/np.sqrt(chi_2[index_chi])
#                    Vbr_err_temp.append(uncertainty) 
#                else:
#                    Vbr_err_temp.append(sd_beta[index_chi][0])
            
            #if chi2 < 3 and pval < 1 and pval > 0.05:
            Vbr_temp.append(p[0]) 
            Vbr_err_temp.append(dp[0])
            chi.append(chi2)
            pvalue.append(pval)
            T_temp.append(T[i - 1])
            T_err_temp_lista.append(T_err[i - 1])
            
            print("%s/%s" % (j, 10))
            
        #aca estan los datos antes de promediar como lista de listas
    
    
        Vbr_lista.append(Vbr_temp)
        Vbr_err_lista.append(Vbr_err_temp)
        T_lista.append(T_temp)
        T_err_lista.append(T_err_temp_lista)
        
        Vbr.append(weightedMean(Vbr_temp, Vbr_err_temp))
        Vbr_err.append(np.sqrt(weightedError(Vbr_temp, Vbr_err_temp)**2))
#            Vbr.append(beta[index_chi][0])
#            Vbr_err.append(sd_beta[index_chi][0])
            
        print("success!: "+ str(i))
        
    
    print(str(time.time() - start) + " seconds")
    
    
    first = 0

    plt.figure(1)
    plt.errorbar(T[first:], Vbr[first:], xerr= T_err[first:], yerr= Vbr_err[first:], fmt='or', capsize= 3)
    plt.grid(True)
    
    linear_model = Model(Linear)
    data = RealData(T[first:], Vbr[first:], sy=Vbr_err[first:])
    odr = ODR(data, linear_model, beta0=[24.3, 0.02])
    out = odr.run()
        
    m = out.beta[0]
    b = out.beta[1]
    m_err = out.sd_beta[0]   
    chi2 = out.res_var
    plt.plot(T, [T[i]*m + b for i in range(len(T))])
    plt.xlabel('Temperature [C]')
    plt.ylabel('Breakdown Voltage [V]')
    
    
    
    plt.figure(2)
    for k in range(len(T_lista)):
        plt.errorbar(T_lista[k], Vbr_lista[k], xerr = T_err_lista[k], yerr = Vbr_err_lista[k], fmt = 'ob', capsize = 3)
    plt.grid(True)
    plt.xlabel('Temperature [C]')
    plt.ylabel('Breakdown Voltage [V]')
    
    print("m = %s pm %s" % (m, m_err))
    print("chi2 = %s" % chi2)
    
    plt.figure(3)
    plt.plot(chi, '.')
    plt.ylabel("Chi^2")
    plt.xlabel("Number of Fit accepted")
    
    plt.figure(4)
    
    plt.ylabel("P-value")
    plt.xlabel("Number of Fit accepted")
    plt.plot(pvalue, '.')
    
    
    chi2_vbr_list = []
    
    for i in range(0, len(T)):
        chi_vbr = 0
        mean = weightedMean(Vbr_lista[i], Vbr_err_lista[i])
        for j in range(0, len(Vbr_lista[i])):
            chi_vbr += ((Vbr_lista[i][j] - mean)/(Vbr_err_lista[i][j]))**2
    
        chi2_vbr_list.append(chi_vbr/(len(Vbr_lista[i]) - 1))
        
    plt.figure(5)
    plt.plot(T, chi2_vbr_list, 'o')
    plt.grid(True)
    plt.xlabel("Temperature [C]")
    plt.ylabel("Chi^2")
    plt.tight_layout(True)
    
    return T, Vbr, T_err, Vbr_err

def CalculateVbrT_intercept():
    
    Vbr = []    
    Vbr_err = []
    chi = []
    pvalue = []
    
    path_R = 'temperatures.txt'
    T = np.loadtxt(path_R, skiprows=1)[:, 5]
    T_err = np.loadtxt(path_R, skiprows=1)[:, 6] 
    
    for i in range(1, folders + 1):
    
        path = '%s/vbr' % i
    
        Vbr_temp = []
        Vbr_err_temp = []
    
        for j in range(1, 6):
            
            path_group = '/%s.txt' % j
            data_vbr = np.loadtxt(path + path_group, skiprows=1)
            V = data_vbr[:, 0]
            I = data_vbr[:, 1]
            V_err = error_V(V, keithley)
            I_err = error_I(I, keithley)
            
            I = [np.sqrt(k) for k in I]
            for k in range(0, len(I)):
                I_err[k] = (I_err[k])/(I[k])
                
            chi_2 = []
            pval = []
            beta = []
            sd_beta = []
            
            for h in range(0, len(V) - 2):
                V_fit = V[h:]
                I_fit = I[h:]
                I_err_fit = I_err[h:]
                V_err_fit = V_err[h:]
                model = Model(Linear)
                data = RealData(I_fit, V_fit, sx=I_err_fit, sy=V_err_fit)
                odr = ODR(data, model, beta0=[24., 0], maxit=1000000)
                out = odr.run()
                
                beta.append(out.beta[1])
                sd_beta.append(out.sd_beta[1])
                chi_2.append(out.res_var)
                pval.append(1 - scipy.stats.chi2.cdf(len(I_fit)*out.res_var, len(I_fit)))
    
    
          
            index = ClosestToOne(chi_2)
            Vbr_temp.append(beta[index])
            Vbr_err_temp.append(sd_beta[index])
            chi.append(chi_2[index])
            pvalue.append(pval[index])
            print("%s/%s" % (j, 6))
            
        Vbr.append(weightedMean(Vbr_temp, Vbr_err_temp))
        Vbr_err.append(weightedError(Vbr_temp, Vbr_err_temp))

        print("success!: "+ str(i))
        
    first = 0

    plt.figure(1)
    plt.errorbar(T[first:], Vbr[first:], xerr= T_err[first:], yerr= Vbr_err[first:], fmt='or', capsize= 3)
    plt.grid(True)
    
    linear_model = Model(Linear)
    data = RealData(T[first:], Vbr[first:], sy=Vbr_err[first:])
    odr = ODR(data, linear_model, beta0=[24.3, 0.02])
    out = odr.run()
        
    m = out.beta[0]
    b = out.beta[1]
    m_err = out.sd_beta[0]   
    chi2 = out.res_var
    plt.plot(T, [T[i]*m + b for i in range(len(T))])
    plt.xlabel('Temperature [C]')
    plt.ylabel('Breakdown Voltage [V]')
    
    print("m = %s pm %s" % (m, m_err))
    print("chi2 = %s" % chi2)
    
    plt.figure(2)
    plt.plot(chi, '.')
    plt.ylabel("Chi^2")
    plt.xlabel("Number of Fit accepted")
    
    plt.figure(3)
    
    plt.ylabel("P-value")
    plt.xlabel("Number of Fit accepted")
    plt.plot(pvalue, '.')
    
    return

def CalculateIDarkT():

    I_dark = []
    I_dark_err = []
    
    path_R = 'temperatures.txt'
    R_dark = np.loadtxt(path_R, skiprows=1)[:, 3]
    R_dark_err = np.loadtxt(path_R, skiprows=1)[:, 4]

    
    for k in range(1, folders + 1):
        
        path_dark = '%s/idark/Bias_30V/4.txt' % k

        data_i_dark = np.loadtxt(path_dark, skiprows=1)
        I_dark_temp = data_i_dark[:, 1]
        I_dark_err_temp = error_I(I_dark_temp, keithley)
            
        I_dark.append(np.mean(I_dark_temp)*1E6)
        I_dark_err.append(np.mean(I_dark_err_temp)*1E6)
    
    
    #plt.figure(3)
    #for k in range(len(I_dark)):
    #    plt.plot(R_dark[k], I_dark[k], '.')
    plt.errorbar(R_dark, I_dark, xerr=R_dark_err, yerr=I_dark_err, fmt='.k', capsize=3)
    plt.xlabel("Temperature [C]")
    plt.ylabel("Dark Current [uA]")
    plt.grid(True)
    plt.yscale('log')
    plt.tight_layout(True)
    
    return


def LED_IICurvesConstantdV():
    
    path_T = 'temperatures.txt'
    T = np.loadtxt(path_T, skiprows=1)[:, 1]
    
    I_LED = []
    I_sipm = []
    I_LED_err = []
    I_sipm_err = []
    
    bias = 30.0
    
    for i in range(1, folders + 1):
        I_LED_temp = []
        I_sipm_temp = []
        for j in range(1, 2):
            data = np.loadtxt('%s/LED/Bias_%sV/%s.txt' % (i, bias, j), skiprows=1)
            I_LED_temp = data[:, 1][1:-1]
            I_sipm_temp = data[:, 0][1:-1]
            I_LED_temp_err = error_I(I_LED_temp, keithley, source=True)
            I_sipm_temp_err = error_I(I_sipm_temp, keithley)

            
        I_LED.append(I_LED_temp)
        I_sipm.append(I_sipm_temp)
        I_LED_err.append(I_LED_temp_err)
        I_sipm_err.append(I_sipm_temp_err)
            
            
    for k in range(len(T)):
        plt.errorbar(I_LED[k], I_sipm[k], xerr = I_LED_err[k], yerr = I_sipm_err[k], fmt = '.', capsize = 3, label="%s degrees" % T[k])
    plt.grid(True)
    plt.legend()
    plt.xlabel('LED Current [A]')
    plt.ylabel('SiPM Current [A]')
    plt.yscale('log')
    plt.xscale('log')
    plt.tight_layout(True)
    
    return
        
        
def LED_IVCurveT():   

    path_T = 'temperatures.txt'
    T = np.loadtxt(path_T, skiprows=1)[:, 1]
    
    I_LED = []
    V_LED = []
    I_LED_err = []
    V_LED_err = []
    
    bias = 30.0
    
    
    for i in range(1, folders + 1):
        I_LED_temp = []
        V_LED_temp = []
        for j in range(1, 2):
            data = np.loadtxt('%s/LED/Bias_%sV/%s.txt' % (i, bias, j), skiprows=1)
            I_LED_temp = data[:, 1]
            V_LED_temp = data[:, 2]
            I_LED_temp_err = error_I(I_LED_temp, keithley, source=True)
            V_LED_temp_err = error_V(V_LED_temp, keithley, source=False)
            
        I_LED.append(I_LED_temp)
        V_LED.append(V_LED_temp)
        I_LED_err.append(I_LED_temp_err)
        V_LED_err.append(V_LED_temp_err)
            
            
    for k in range(len(T)):
        plt.errorbar(I_LED[k], V_LED[k], xerr = I_LED_err[k], yerr = V_LED_err[k], fmt = '.', capsize = 3, label="%s degrees" % T[k])
    plt.grid(True)
    plt.xlabel('LED Current [A]')
    plt.ylabel('LED Voltage [V]')
    plt.legend()
    plt.tight_layout(True)
            
    return

def LED_ISIPMT():
    path_T = 'temperatures.txt'
    T = np.loadtxt(path_T, skiprows=1)[:, 1]
    T_err = np.loadtxt(path_T, skiprows=1)[:, 2]
    
    I_sipm = []
    I_LED = []
    
    I_list = [0, 25, 50, 75, 99]
    bias = 30.0
    
    for k in range(1, len(T) + 1):
        data = np.loadtxt('%s/LED/Bias_%sV/1.txt' % (k, bias), skiprows=1)
        I_sipm.append(data[:, 0])
        I_LED.append(data[:, 1])
    
    for j in range(0, len(I_list)):
        y_plot = []
        for k in range(0, len(T)):
            index = np.where(I_LED[k] == I_LED[k][I_list[j]])[0][0]
            y_plot.append(I_sipm[k][index])
            
        y_plot_err = error_I(y_plot, keithley, source=False)
        
        value = I_LED[0][I_list[j]]*pow(10, 3)
        
        plt.errorbar(T, y_plot, xerr=T_err, yerr=y_plot_err, fmt='o', label="%s mA" % value)
        
    plt.grid(True)
    plt.yscale('log')
    plt.xlabel('Temperature [C]')
    plt.ylabel('SiPM Current [A]')
    plt.legend()
    plt.tight_layout(True)

    return

def LED_IIOVERVOLTAGE():
    path_T = 'temperatures.txt'
    T = np.loadtxt(path_T, skiprows=1)[:, 1]
    
    V_list = [29.4, 29.6, 29.8, 30.0]
    T = 1
    
    i = 0
    f = 100
    
    for k in range(0, len(V_list)):
        data = np.loadtxt('%s/LED/Bias_%sV/1.txt' % (T, V_list[k]), skiprows=1)
        I_sipm = data[i:f, 0][i:f]
        I_LED = data[i:f, 1][i:f]
        I_sipm_err = error_I(I_sipm, keithley, source=False)
        I_LED_err = error_I(I_LED, keithley, source=True)
        
        plt.errorbar(I_LED, I_sipm, xerr=I_LED_err, yerr=I_sipm_err, fmt='o', label="%s V" % V_list[k])
        
    plt.grid(True)
    plt.yscale('log')
    plt.xlabel('LED Current [A]')
    plt.ylabel('SiPM Current [A]')
    plt.xscale('log')
    plt.legend()
    plt.tight_layout(True)

    return

def LED_DARKCURRENTOVERVOLTAGE():
    path_T = 'temperatures.txt'
    T = np.loadtxt(path_T, skiprows=1)[:, 1]
    T_err = np.loadtxt(path_T, skiprows=1)[:, 2]
    
    V_list = [29.4, 29.6, 29.8, 30.0]
    
    Dark_current = []
    Dark_current_err = []
    
    for i in range(0, len(V_list)):
        
        i_temp = []
        i_err_temp = []
        
        for j in range(1, folders + 1):
            data = np.loadtxt('%s/LED/Bias_%sV/1.txt' % (j, V_list[i]), skiprows=1)
            
            current = data[:, 0][0:15]
            current_err = data[:, 3][0:15]
            
            i_temp.append(np.mean(current))
            i_err_temp.append(np.mean(current_err))
            
        Dark_current.append(i_temp)
        Dark_current_err.append(i_err_temp)     
        
    for k in range(0, len(V_list)):   
        plt.errorbar(T, Dark_current[k], xerr=T_err, yerr=Dark_current_err[k], fmt='o', label="SiPM polarized at %s V" % V_list[k])
        
    plt.grid(True)
    plt.yscale('log')
    plt.xlabel('Temperature [C]')
    plt.ylabel('SiPM Current [A]')
    plt.legend()
    plt.tight_layout(True)

    return

def LED_ILEDT():
    path_T = 'temperatures.txt'
    T = np.loadtxt(path_T, skiprows=1)[:, 1]
    T_err = np.loadtxt(path_T, skiprows=1)[:, 2]
    
    I_sipm = []
    V_LED = []
    
    I_list = [1, 25, 50, 99]
    bias = 30.0
    
    for k in range(1, len(T) + 1):
        data = np.loadtxt('%s/LED/Bias_%sV/1.txt' % (k, bias), skiprows=1)
        I_sipm.append(data[:, 0])
        V_LED.append(data[:, 2])
    
    for j in range(0, len(I_list)):
        y_plot = []
        for k in range(0, len(T)):
            index = np.where(I_sipm[k] == I_sipm[k][I_list[j]])[0][0]
            y_plot.append(V_LED[k][index])
            
        y_plot_err = error_I(y_plot, keithley, source=False)
        
        value = I_sipm[0][I_list[j]]*pow(10, 3)
        
        plt.errorbar(T, y_plot, xerr=T_err, yerr=y_plot_err, fmt='o', label="%s mA" % round(value, 4))
        
    plt.grid(True)
    #plt.yscale('log')
    plt.xlabel('Temperature [C]')
    plt.ylabel('LED Voltage [V]')
    plt.legend()
    plt.tight_layout(True)

    return

def CURRENTDRIFT():
    
    def Exponential(M, x):
        m, b = M
        return b*np.exp(m*x)
    
    def ClosestToValue(v, value):
        compliance = []
        for j in range(0, len(v)):
            compliance.append(abs(v[j] - value))
        return compliance.index(np.min(compliance))
    
    def DetectIndeces(v):
        index_hi = [0]
        index_lo = []
        out_hi = []
        out_lo = []
        
        for i in range(1, len(v) - 1):
            if v[i + 1] - v[i] > 100E-6:
                index_hi.append(i + 1)
            if v[i] - v[i + 1] > 100E-6:
                index_lo.append(i + 1)
                
        for i in range(0, len(index_lo)):
                
            if i != len(index_lo) - 1:
                out_hi.append([index_hi[i], index_lo[i] - 1])       
                out_lo.append([index_lo[i], index_hi[i + 1] - 1])       
            else:
                out_hi.append([index_hi[i], index_lo[i] - 1])       
                out_lo.append([index_lo[i], len(v) - 1])                      
    
        return out_lo, out_hi

    os.chdir(home_path)
    data = np.loadtxt("results/Encapsulado_%s/delay/7.txt" % encapsulado, skiprows=1)
    
    time_sipm = data[:, 0]
    
    I_sipm = data[:, 1]
    I_sipm_err = data[:, 4]
    
    I_led = data[:, 3]
    I_led_err = data[:, 5]
    
    #CAUTION! V_led in not in every measurement. only in 8 and up
#    V_led = data[:, 6]
#    V_led_err = data[:, 7]
    
    lists = DetectIndeces(I_led)
    lo = lists[0]
    hi = lists[1]

    tolerance_relax = 3.15E-6
    
    
    I_led_hi = []
    I_led_hi_err = []
    #I_led_lo = []
    #I_led_lo_err = []
    for i in range(0, len(hi)):
        I_led_hi.append(np.mean(I_led[hi[i][0]:hi[i][1]]))
        I_led_hi_err.append(np.sqrt(np.mean(I_led_err[hi[i][0]:hi[i][1]])**2 + np.std(I_led[hi[i][0]:hi[i][1]])**2))
    #    I_led_lo.append(np.mean(I_led[lo[i][0]:lo[i][1]]))
    #    I_led_lo_err.append(np.sqrt(np.mean(I_led_err[lo[i][0]:lo[i][1]])**2 + np.std(I_led[lo[i][0]:lo[i][1]])**2))
    
    
    slope = []
    slope_err = []
    chi2 = []
    model = Model(Linear)
    for i in range(0, len(hi)):
        start = hi[i][0] + 100
        end = hi[i][1] 
        data = RealData(time_sipm[start:end], I_sipm[start:end], sy=I_sipm_err[start:end])
        odr = ODR(data, model, beta0=[0., 0.], maxit=100000)
        out = odr.run()
        
        slope.append(out.beta[0])
        slope_err.append(out.sd_beta[0])
        chi2.append(out.res_var)
        
    
    jump = []
    jump_err = []
    for i in range(0, len(I_led_hi)):
        value = I_sipm[hi[i][1]] - I_sipm[lo[i][0]]
        jump.append(value)
        jump_err.append(np.sqrt(I_sipm_err[hi[i][1]]**2 + I_sipm_err[lo[i][0]])**2)
        
    
    relax = []
    for i in range(0, len(I_led_hi)):

        I = I_sipm[lo[i][0]:lo[i][1]]
        t = time_sipm[lo[i][0]:lo[i][1]]
        
        index = ClosestToValue(I, tolerance_relax)
        relax.append(t[index] - t[0])
        
    overshoot = []
#    overshoot_err = []
    for i in range(0, len(I_led_hi)):
        value = I_sipm[hi[i][0]] - np.min(I_sipm[hi[i][0]:hi[i][1]]) 
        overshoot.append(value)
#        overshoot_err.append(np.sqrt(I_sipm_err[hi[i][1]]**2 + I_sipm_err[lo[i][0]])**2)     
    
       
    I_led_hi = [1E6*i for i in I_led_hi]
    I_led_hi_err = [1E6*i for i in I_led_hi_err]
    slope = [1E6*i for i in slope]
    slope_err = [1E6*i for i in slope_err]
    
    
    model = Model(Exponential)
    data = RealData(I_led_hi, slope, sx=I_led_hi_err, sy=slope_err)
    odr = ODR(data, model, beta0=[0., 0.], maxit=100000)
    out = odr.run()
    
    x = np.linspace(200E-6, 215E-6)
    
    plt.figure(1)
    plt.errorbar(I_led_hi, slope, xerr=I_led_hi_err, yerr=slope_err, fmt='.k', capsize=3)
    #plt.plot(x, Exponential(out.beta, x))
    plt.xlabel("LED Current [uA]")
    plt.ylabel("Current updrift when output is ON [uA]")
    plt.yscale('log')
    plt.grid(True)
    plt.tight_layout(True)
    
    
    plt.figure(2)
    plt.errorbar(I_led_hi, relax, xerr=I_led_hi_err, fmt='.k', capsize=3)
    #plt.plot(x, Exponential(out.beta, x))
    plt.xlabel("LED Current [uA]")
    plt.ylabel("Time to reach dark current after output is turned OFF [uA]")
    plt.yscale('log')
    plt.grid(True)
    plt.tight_layout(True)
    
    
    
#    plt.figure(3)
#    plt.errorbar(I_led_hi, jump, xerr=I_led_hi_err, yerr=jump_err, fmt='.k', capsize=3)
#    #plt.plot(x, Exponential(out.beta, x))
#    plt.xlabel("LED Current [uA]")
#    plt.ylabel("Current discontinuity jump when output is turned OFF [uA]")
#    plt.yscale('log')
#    plt.grid(True)
#    plt.tight_layout(True)
    
    plt.figure(3)
    plt.errorbar(I_led_hi, overshoot, xerr=I_led_hi_err, fmt='.k', capsize=3)
    #plt.plot(x, Exponential(out.beta, x))
    plt.xlabel("LED Current [uA]")
    plt.ylabel("Current Overshoot when output is turned ON [uA]")
    plt.yscale('log')
    plt.grid(True)
    plt.tight_layout(True)
    
    #plt.figure(4)
    #plt.plot(I_led_hi, chi2, 'ok', )
    #plt.plot()
    #plt.xlabel("LED Current [uA]")
    #plt.ylabel("Fit chi^2")
    #plt.grid(True)
    #plt.tight_layout(True)
    
    return

#%% MENUS

ans = True
while ans:
    print ("\nLabOSat measurement analysis menu\n\n1. LED experiments\n2. Rq experiments\n3. Vbr experiments\n4. Dark Current experiments\n5. Exit")
    ans=str(input("Select an option: "))
    if ans == "1": 
        print("\nLED experiments menu\n\n1. I-I Curves for various T (range: -40 to 40 degrees)\n2. LED IV Curves for various T (range: -40 to 40 degrees)\n3. Isipm vs T curves for various ILED\n4. VLED vs T curves for various Isipm\n5. I-I Curves for various overvoltages (fixed T)\n6. Dark current vs T for various overvoltages\n7. Current Drift Experiments\n8. Return") 
        ans=str(input("Select an option: "))
        if ans == "1":
            LED_IICurvesConstantdV()
            ans = False
        elif ans == "2":
            LED_IVCurveT()
            ans = False
        elif ans == "3":
            LED_ISIPMT()
            ans=False
        elif ans == "4":
            LED_ILEDT()
            ans = False
        elif ans == "5":
            LED_IIOVERVOLTAGE()
            ans = False
        elif ans == "6":
            LED_DARKCURRENTOVERVOLTAGE()
            ans = False
        elif ans == "7":
            CURRENTDRIFT()
            ans = False
        elif ans == "8":
            continue
        else:
            print("\nInvalid input.\n")
    elif ans == "2":
        print("\nRq experiments menu\n\n1. Rq(T) curve\n2. Return") 
        ans=str(input("Select an option: "))
        if ans == "1":
            CalculateRqT()
            ans = False
        elif ans == "2":
            continue
        else:
            print("\nInvalid input.\n") 
    elif ans=="3":
        print("\nVbr experiments menu\n\n1. Vbr(T) (1/x fit method)\n2. Vbr(T) (sqrt I intercept method)\n3. Return") 
        ans=str(input("Select an option: "))
        if ans == "1":
            CalculateVbrT_fit()
            ans = False
        elif ans == "2":
            CalculateVbrT_intercept()
            ans = False
        elif ans == "3":
            continue
        else:
            print("\nInvalid input.\n") 
    elif ans == "4":
        print("\nDark Current experiments menu\n\n1. Dark Current(T)\n2. Return") 
        ans=str(input("Select an option: "))
        if ans == "1":
            CalculateIDarkT()
            ans = False
        elif ans == "2":
            continue
        else:
            print("\nInvalid input.\n") 
    elif ans == "5":
      ans = False
    else:
      print("\n Invalid input.") 
      
    
#encapsulado = 1
#enc_try = 2
#
#folders = DetectFolders('results/Encapsulado_%s_try%s/' % (str(encapsulado), str(enc_try)))
#T1, Vbr1, T1_err, Vbr1_err = CalculateVbrT()
#
#encapsulado = 1
#enc_try = 3
#
#folders = DetectFolders('results/Encapsulado_%s_try%s/' % (str(encapsulado), str(enc_try)))
#T2, Vbr2, T2_err, Vbr2_err = CalculateVbrT()
#
#T = np.concatenate((T1, T2))
#Vbr = np.concatenate((Vbr1, Vbr2))
#T_err = np.concatenate((T1_err, T2_err))
#Vbr_err = np.concatenate((Vbr1_err, Vbr2_err))

#%%

#Vbr = [24.822, 24.675, 24.535, 24.348, 24.185, 24.051, 23.91, 23.791, 23.632, 25.025, 25.162]
#Vbr_err = [0.004, 0.0040719, 0.0040616, 0.0046318, 0.0071298, 0.023444, 0.0149, 0.020699,
#           0.03039, 0.0052192, 0.0056791]
#Vbr_MC = [24.83, 24.6753, 24.5346, 24.3471, 24.1853, 24.0506, 23.9109, 23.7903, 23.6314,
#          25.0365, 25.165]
#Vbr_MC_err = [0.062, 0.00392235, 0.00437468, 0.00462331, 0.00437246, 0.00566965, 0.00468052,
#              0.00526044, 0.00532189, 0.0706271, 0.065173]
#
#def Linear(M, x):
#    m, b = M
#    return m*x + b
#
##p2 goes around 1.69 instead of 2
#
#
#T = np.loadtxt("C:/Users/lucas/Desktop/LabOSat CAC/results/Encapsulado_1_try3/temperatures.txt", skiprows=1)[:, 1]
#T_err = np.loadtxt("C:/Users/lucas/Desktop/LabOSat CAC/results/Encapsulado_1_try3/temperatures.txt", skiprows=1)[:, 2]
#
#import matplotlib.pyplot as plt
#plt.errorbar(T, Vbr, xerr=T_err, yerr=Vbr_err, fmt='.k', capsize=3)
#
##plt.errorbar(T, Vbr_MC, xerr=T_err, yerr=Vbr_MC_err, fmt='.', capsize=3, color='red')
#
#
#linear_model = Model(Linear)
#data = RealData(T, Vbr, sx=T_err, sy=Vbr_err)
#odr = ODR(data, linear_model, beta0=[0.02, 24.])
#out = odr.run()
#    
#m = out.beta[0]
#b = out.beta[1]
#b_err = out.sd_beta[1]   
#m_err = out.sd_beta[0]
#chi2 = out.res_var
#plt.plot(T, [T[i]*m + b for i in range(len(T))])
#
#
#print("m = %s +/- %s mV" % (m*1000, m_err*1000))
#print("red. chi2 = %s" % out.res_var)
      