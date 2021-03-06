''' This is the one in which I match the whole table!
and also save a couple of columns' data to, like, a file so that
I can access it all easy-like later
'''

import atpy 
import numpy, math
import matplotlib.pyplot as plt
import coords

where = numpy.where

boxsize_as = 1. #size, in arcseconds, that the best matches will come from
boxsize = boxsize_as/3600. # boxsize in degrees

print "box size for selection is %f arcsec" % boxsize_as

data = '/home/trice/reu/DATA/Merged_Catalogs/'
data2= '/home/trice/reu/DATA/2MASS/'

# Does ATpy have options to suppress output for these fits files?

Userv= atpy.Table(data+'USERV1678_error_filtered_0.1.fits',verbose=False)
#u08b = atpy.Table(data+'U08BH2_error_filtered_0.1.fits',verbose=False)
#u09b = atpy.Table(data+'U09BH14_error_filtered_0.1.fits',verbose=False)
Tmass= atpy.Table(data2+'fp_2mass.fp_psc26068.tbl',verbose=False)
#iras = atpy.Table(data2+'iras.iraspsc26148.tbl',verbose=False)

Output = atpy.Table() #Output is my output table!

delta = math.cos(math.radians(Tmass.dec.mean()))

#brights = numpy.where(Tmass.j_m < 10)[0]
#print brights

min_offset = -0.1* numpy.ones_like(Tmass.ra)
match =  -1* numpy.ones_like(Tmass.err_ang) #the only reason I use err_ang is because I want "match" to be an integer array, this might be irrelevant

counter = 1

for s1 in range(Tmass.ra.shape[0]):
    print "================ Source number %d: ================" % counter

    
    c1 = coords.Position((Tmass.ra[s1],Tmass.dec[s1]))
    print "Coordinates: ", c1
    #WFCAM is still in radians!!!
    # let's take the intersection of these four where queries
    w1= where(numpy.degrees(Userv.DEC) < Tmass.dec[s1] + boxsize)[0]
    w2= where(numpy.degrees(Userv.DEC) > Tmass.dec[s1] - boxsize)[0]
    w3= where(numpy.degrees(Userv.RA)  < Tmass.ra[s1] + boxsize/delta)[0]
    w4= where(numpy.degrees(Userv.RA)  > Tmass.ra[s1] - boxsize/delta)[0]

    rabox = numpy.intersect1d(w3,w4)
    decbox= numpy.intersect1d(w1,w2)

    box = numpy.intersect1d(rabox,decbox)
    
#    print box, "these guys got matched"

    offset = -1.* numpy.ones_like(Userv.RA[box])
    if offset.size != 0:
        for s2 in range(Userv.RA[box].shape[0]):
            # Don't forget! WFCAM data comes in radians!
            c2 = coords.Position((Userv.RA[box][s2],Userv.DEC[box][s2]),units='radians')
            offset[s2] = c1.angsep(c2).arcsec()
        
    #print "The min,max,mean offset: ", str(offset.min()), str(offset.max()), str(offset.mean()) #all in arcsec

        min_offset[s1] = offset.min()

        print "Offset to best match: %f arcsec" % min_offset[s1]
        match[s1] = box[numpy.where(offset == offset.min())][0]
        print "Index number of catalog 2 source match: %s" % str(match[s1])
#numpy.where(offset.min())
    #print Userv.data[match]
    #try also Userv.row(match)

        print "2MASS jmag: "+str(Tmass.j_m[s1])
        print "WFCAM jmag: "+str(Userv.JAPERMAG3[match[s1]])
    else:
        print "No match found within %d arcsec" % boxsize_as
    counter += 1
    #if counter == 100: break

print "finished successfully"

Output.add_column('match',match)
Output.add_column('offset',min_offset,unit='arcsec')


Output.write('test_output.fits',overwrite=True)

plt.hist(min_offset,500,range=(0,2))
plt.show()
