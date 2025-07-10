import numpy as np
import os

os.chdir("C:/Users/lucas/Desktop/LabOSat CAC/")

from functions import error_I, error_V, LogData, DiffData

encapsulado = 1
enc_try = 3
i = 9
j = 1

path = 'results/Encapsulado_%s_try%s/%s/vbr' % (encapsulado, enc_try, i)

path_group = '/%s.txt' % j
data_vbr = np.loadtxt(path + path_group, skiprows=1)
V = data_vbr[:, 0]
I = data_vbr[:, 1]
V_err = error_V(V, '2602')
I_err = error_I(I, '2602')


V, I, I_err = LogData(V, I, I_err)
V, I, V_err, I_err = DiffData(V, I, V_err, I_err)


#flag to check if data needs to be inverted
I = I[10:-70]
V = V[10:-70]
I_err = I_err[10:-70]
V_err = V_err[10:-70]

if abs(np.max(I)) > abs(np.min(I)):
    index = I.index(np.max(I))
elif abs(np.max(I)) < abs(np.min(I)):
    index = I.index(np.min(I))
    I = [-x for x in I]
    
np.savetxt("C:/Users/lucas/Desktop/1.txt", np.c_[V[index:], I[index:], V_err[index:], I_err[index:]])