import matplotlib.pyplot as plt
import numpy as np
from scipy.odr import ODR, Model, RealData
import os
import scipy.stats


# I use an exponential function which is analogous to a point to point interpolation
# FITS OK except last point at ambient T

def fit_function(M, x):
    a, b = M
    return a*np.log(b*x)

home_path = "C:/Users/LINE/Desktop/LabOSat CAC/"
os.chdir(home_path)

from functions import DetectFolders, error_I, error_V, Linear

encapsulado = 3

#number of try (or measurement set) for said package
enc_try = 2

folders = DetectFolders("results/Encapsulado_2/sd_test_1/")

os.chdir("results/Encapsulado_2/sd_test_1/")

I_dark = []
I_dark_err = []

path_R = 'temperatures.txt'
R_dark = np.loadtxt(path_R, skiprows=1)[:, 3]
R_dark_err = np.loadtxt(path_R, skiprows=1)[:, 4]

for k in range(1, folders + 1):
    
    path_dark = '%s/idark/Bias_30V/4.txt' % k

    data_i_dark = np.loadtxt(path_dark, skiprows=1)
    I_dark_temp = data_i_dark[:, 1]
    I_dark_err_temp = error_I(I_dark_temp, '2602')
        
    I_dark.append(np.mean(I_dark_temp))
    I_dark_err.append(np.mean(I_dark_err_temp))
    
#R_dark, I_dark, I_dark_err = LogData(R_dark, I_dark, I_dark_err)
    
plt.figure(1)
plt.plot(I_dark, R_dark, 'o')


model = Model(fit_function)
data = RealData(I_dark, R_dark, sx=I_dark_err, sy=R_dark_err)
odr = ODR(data, model, beta0=[0.1, 0.1], maxit=100000000)
out = odr.run()

params = out.beta    
chi = out.res_var
pvalue = 1 - scipy.stats.chi2.cdf(len(R_dark)*out.res_var, len(R_dark))

I_dark =np.asarray(I_dark)


plt.plot(I_dark, fit_function(params, I_dark))
#plt.yscale('log')

print("Reduced Chi sq: %s, p-value: %s" % (chi, pvalue))

os.chdir(home_path)
data = np.loadtxt("results/Encapsulado_%s/sd_test_%s/dark_currents.txt" % (str(encapsulado), str(enc_try)), skiprows=3, comments='#')


x = data[:,  5]
x_err = data[:, 6]
    
b = np.arange(0, len(x), 1)
x_calibrated = [fit_function(params, x[j]*1E-6) for j in b]
x_err_calibrated = [params[0]*x_err[j]/x[j] for j in b]    
    
    
    