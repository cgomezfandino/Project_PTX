import numpy as np
# 212

dicti = {'Momemtum':{}}

b = ['backtest1','back2']

r = ['beta','alpha','gamma']
n = range(0,3,1)
x = dict(zip(n,r))
print x
# for i in enumerate(b):
dicti['Momemtum']['backtest_%i'] = x

print dicti

# a= ['riesgo1','riesgo2','riesgo3']
#
#
# # dicti[0]
#
# dicti['Momemtum']['tres'] = 5
# print(dicti)