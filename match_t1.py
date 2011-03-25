import atpy 
import numpy
import matplotlib.pyplot as plt
import coords

data = '/home/trice/reu/DATA/Merged_Catalogs/'
data2= '/home/trice/reu/DATA/2MASS/'

# Does ATpy have options to suppress output for these fits files?

userv= atpy.Table(data+'USERV1678_error_filtered_0.1.fits')
u08b = atpy.Table(data+'U08BH2_error_filtered_0.1.fits')
u09b = atpy.Table(data+'U09BH14_error_filtered_0.1.fits')
tmass= atpy.Table(data2+'fp_2mass.fp_psc26068.tbl')
iras = atpy.Table(data2+'iras.iraspsc26148.tbl')

# I am going to brute this now and later figure out the most elegant 
# array-based solution; for now I just want working code.

'''
## This doesn't actually work:

# The array of coordinates for 2mass
tmass.co = numpy.zeros_like(tmass.ra)
for i in range(tmass.co.shape[0]):
    tmass.co[i] = coords.Position([tmass.ra[i],tmass.dec[i]])

# The array of coordinates for userv
userv.co = numpy.zeros_like(userv.RA)
for i in range(userv.co.shape[0]):
    userv.co[i] = coords.Position([userv.RA[i],userv.DEC[i]])
'''

# The following is a test: let's take the brightest 2mass 
# source and find his match
print numpy.where(tmass.j_m == tmass.j_m.min())

# Next time I'll say "for s1 in range(tmass.ra.shape[0])" or something

s1 = numpy.where(tmass.j_m == tmass.j_m.min())[0][0]
print s1

offset = numpy.zeros_like(userv.RA)
for s2 in range(userv.RA.shape[0]):
    c1 = coords.Position((tmass.ra[s1],tmass.dec[s1]))
    # Don't forget! WFCAM data comes in radians!
    c2 = coords.Position((userv.RA[s2],userv.DEC[s2]),units='radians')
    offset[s2] = c1.angsep(c2).arcsec()

print "The min,max,mean offset: ", str(offset.min()), str(offset.max()), str(offset.mean()) #all in arcsec
match = numpy.where(offset == offset.min())
print match
#numpy.where(offset.min())
print userv.data[match]

print "2MASS jmag: "+str(tmass.j_m[s1])
print "WFCAM jmag: "+str(userv.JAPERMAG3[match])
