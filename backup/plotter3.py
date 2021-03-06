import atpy
import numpy
import matplotlib.pyplot as plt

data = '/home/trice/reu/DATA/'

# don't forget: 0 mag is brighter than 30 mag

t = atpy.Table(data+'results14_22_20_4_15864.fits')

j = t.JAPERMAG3
h = t.HAPERMAG3
k = t.KAPERMAG3

mag = [j,h,k]

#for i in mag:
#    i[i<0] = -100
j[j<0] = -100
h[h<0] = -200
k[k<0] = -300


plt.plot(h-k,j,'ro')
plt.ylabel("J magnitude")
plt.xlabel("H-K color")
plt.title("Braid nebula region H-K vs J, U08B")
#plt.axis([35,5,28,8])

plt.show()
