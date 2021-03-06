""" Make a spreadsheet of lots of data. 

The purpose of this module is to calculate global statistics for 
the time-series data of many stars, such as mean magnitudes, RMS variability,
the Stetson variability index, (optionally) best-fit periods, etc,
and to bundle all of these values up into a spreadsheet. It's really useful!

Useful functions:
  spreadsheet_write - Creates a statistics spreadsheet of many stars
  spread_write_test - a testing function for spreadsheet_write; useful
                      for quantifying the performance of spreadsheet_write
  base_lookup - creates a simple lookup table.

Helper functions:
  arraystat_2 - calculates a large number of stats for one star
  reduced_chisq - calculates the reduced chi-square for an array and its 
                  errors
  make_sidset - takes a table with repeated IDs and gives a list of unique IDs
                contained therein
"""

import atpy
import numpy as np
import stetson
import robust as rb
from tr_helpers import data_cut
from scargle import fasper as lsp
from timing import lsp_mask
from chi2 import test_analyze
from network2 import get_chip


def reduced_chisq ( m, sigma_m ):
    """ Calculates the reduced chi-squared.

    Inputs:
      m -- an array of photometric magnitudes
      sigma_m -- a corresponding array of photometric uncertainties
      """

    if not (m.size == sigma_m.size):
        raise Exception("Array dimensions mismatch")

    n = m.size
    nu = n - 1

    if n < 2:
        return 0

    return (1./nu) * np.sum( (m - m.mean())**2 / sigma_m**2 )



def arraystat_2 (table, sid, season=0, rob=True, per=True, flags=0) :
    """ Calculates a complicated number of parameters for a given star.

    Inputs:
      table -- an ATpy table with time-series photometry
      sid -- a WFCAM source ID.
      
    Optional inputs:
      season -- which season to select (1,2,3, or other=All)
      rob -- also use Robust statistics? (takes longer, default True)
      per -- run period-finding? (takes longer, default True)
      flags -- Maximum ppErrBit quality flags to use (default 0)

    Returns:
      ret -- a data structure containing the computed values.
      """
    
    s_table = data_cut( table, [sid], season=season, flags=flags )

    if len(s_table) < 1:
        print "no data for %d!" % sid
        return None
    
    jcol = s_table.JAPERMAG3; jerr = s_table.JAPERMAG3ERR
    hcol = s_table.HAPERMAG3; herr = s_table.HAPERMAG3ERR
    kcol = s_table.KAPERMAG3; kerr = s_table.KAPERMAG3ERR
    jmhcol=s_table.JMHPNT   ; jmherr = s_table.JMHPNTERR
    hmkcol=s_table.HMKPNT   ; hmkerr = s_table.HMKPNTERR
    racol= s_table.RA
    decol= s_table.DEC

    date = s_table.MEANMJDOBS 

    messy_table = data_cut( table, [sid], season=-1 )
    jppcol=messy_table.JPPERRBITS
    hppcol=messy_table.HPPERRBITS
    kppcol=messy_table.KPPERRBITS

    # make an empty data structure and just assign it information, then return 
    # the object itself!!! then there's no more worrying about indices.
    class Empty():
        pass

    ret = Empty()
    
    ret.N = len(s_table)
    ret.RA = racol.mean()
    ret.DEC = decol.mean()
    
    ret.chip = get_chip(date[0], np.degrees(racol[0]), np.degrees(decol[0]))
    if ret.N > 4:
        ret.one_chip = ( get_chip(date[0], racol[0], decol[0]) ==
                         get_chip(date[1], racol[1], decol[1]) ==
                         get_chip(date[2], racol[2], decol[2]) ==
                         get_chip(date[3], racol[3], decol[3]) )
    else:
        ret.one_chip = True
    
    ret.Stetson = stetson.S(jcol, jerr, hcol, herr, kcol, kerr)
    
    ret.j = Empty();   ret.j.data = jcol;   ret.j.err = jerr
    ret.h = Empty();   ret.h.data = hcol;   ret.h.err = herr
    ret.k = Empty();   ret.k.data = kcol;   ret.k.err = kerr
    ret.jmh = Empty(); ret.jmh.data=jmhcol; ret.jmh.err = jmherr
    ret.hmk = Empty(); ret.hmk.data=hmkcol; ret.hmk.err = hmkerr

    bands = [ ret.j, ret.h, ret.k, ret.jmh, ret.hmk ]

    for b in bands:
        # use b.data, b.err
        
        b.rchi2 = reduced_chisq( b.data, b.err )

        b.mean = b.data.mean()
        b.rms = b.data.std()
        b.min = b.data.min()
        b.max = b.data.max()
        b.peak_trough = b.max - b.min

        b.mean_err = b.err.mean()

        # Robust quantifiers simply have an "r" at the end of their names
        if rob:
            b.datar = rb.removeoutliers(b.data, 3, niter=2)
            
            b.meanr = rb.meanr(b.data)
            b.rmsr = rb.stdr(b.data)
            b.minr = b.datar.min()
            b.maxr = b.datar.max()
            b.peak_troughr = b.maxr - b.minr

        # Period finding... is a little dodgy still, and might take forever
        if per:
            
            b.lsp = lsp(date, b.data, 6., 6.) # apologies if this is cluttered
            Jmax = lsp_mask(b.lsp[0], b.lsp[1])
            b.lsp_per = 1./ b.lsp[0][Jmax]
            b.lsp_pow = b.lsp[1][Jmax]
            b.fx2_per = 1./ test_analyze( date, b.data, b.err )

    # Finally we'll want to do the whole slope, distance on the JMH graph
    # (until I get the fitting done, we'll have to use hmk and jmh naively)
    ret.color_slope = (ret.jmh.peak_trough / ret.hmk.peak_trough)
    


    # and the pp_max, using the messy table
    ret.jpp_max = jppcol.max()
    ret.hpp_max = hppcol.max()
    ret.kpp_max = kppcol.max()

    return ret

def make_sidset ( table ) :
    """ Returns an array of unique source IDs."""

    return np.array(list(set(table.SOURCEID)))

    
def base_lookup (table):
    """ makes a really basic lookup table if you're too lazy"""

    sidarr = np.array( list( set( table.SOURCEID ) ) )
    names = sidarr - 44027700000000L

    Lookup = atpy.Table()
    Lookup.add_column("SOURCEID", sidarr)
    Lookup.add_column("Designation", names )

    return Lookup


def spreadsheet_write (table, lookup, season, outfile, flags=0,
                       Test=False, rob=False, per=False):
    """ 
    Makes my spreadsheet! Basically with a big forloop.

    Inputs:
      table -- an ATpy table with time-series photometry
      lookup -- an ATpy table of interesting sources and their designations
      season -- which season to select (1,2,3, or other=All)
      outfile -- where to save the output table
      
    Optional inputs:
      flags -- Maximum ppErrBit quality flags to use (default 0)
      Test -- whether to exit after 30 sources (default False)
      rob -- also use Robust statistics? (takes longer, default False)
      per -- run period-finding? (takes longer, default False)

    Returns:
      None (but writes an output file to `outfile`)

    Note: crashes if given any stars with only 1 observation and per=True.
    """

    sidarr = lookup.SOURCEID
    names = lookup.Designation
    l = sidarr.size


    Output = atpy.Table()

    N = np.ones_like(sidarr)
    RA = np.ones(l)
    DEC= np.ones(l)
    chip = np.ones_like(sidarr)
    one_chip = np.ones_like(sidarr==sidarr)
    
    Stetson = np.ones(l)
    
    class Band:
        pass

    j = Band()
    h = Band()
    k = Band()
    jmh = Band()
    hmk = Band()

    bands = [ j, h, k, jmh, hmk ]
    band_names = ['j', 'h', 'k', 'jmh', 'hmk']
   
    for b in bands:
        b.mean = np.ones(l)
        b.rms =  np.ones(l)
        b.rchi2 =np.ones(l)
        b.min =  np.ones(l)
        b.max =  np.ones(l)
        b.peak_trough =  np.ones(l)
        
        b.meanr =  np.ones(l)
        b.rmsr =  np.ones(l)
        b.minr =  np.ones(l)
        b.maxr =  np.ones(l)
        b.peak_troughr =  np.ones(l)
        
        # per:
        b.lsp_per =  np.ones(l)
        b.lsp_pow =  np.ones(l)
        b.fx2_per =  np.ones(l)
    
    color_slope =  np.ones(l)
    jpp_max = np.ones_like(sidarr)
    hpp_max = np.ones_like(sidarr)
    kpp_max = np.ones_like(sidarr)
        

    for sid, i in zip(sidarr, range(len(sidarr)) ):

        # v for values
        v = arraystat_2 (table, sid, season, rob, per, flags=flags)
        if v == None:
            #skip assigning anything!
            continue
        vbands = [v.j, v.h, v.k, v.jmh, v.hmk]
        vband_names = ['v.j', 'v.h', 'v.k', 'v.jmh', 'v.hmk']

        N[i] = v.N
        RA[i] = v.RA
        DEC[i] = v.DEC
        chip[i] = v.chip
        one_chip[i] = v.one_chip
        Stetson[i] = v.Stetson

        for b, bn, vb, vbn in zip(bands, band_names, vbands, vband_names):
            
#            print "writing into band " + repr(b) + " with band " + str(vb)
#            print "writing into band %s with band %s" % (bn, vbn)

            b.mean[i] = vb.mean
#            print "mean: " + str(vb.mean)
#            print "recorded mean: " + str(b.mean[i])
#            return
            b.rms[i] = vb.rms
            b.min[i] = vb.min
            b.max[i] = vb.max
            b.peak_trough[i] = vb.peak_trough

            b.rchi2[i] = vb.rchi2

#            b.mean_err[i] = vb.mean_err
            
            if rob:
                b.meanr[i] = vb.meanr
                b.rmsr[i] = vb.rmsr
                b.maxr[i] = vb.maxr
                b.minr[i] = vb.minr
                b.peak_troughr[i] = vb.peak_troughr

            if per:
                b.lsp_per[i] = vb.lsp_per
                b.lsp_pow[i] = vb.lsp_pow
                b.fx2_per[i] = vb.fx2_per
    
        color_slope[i] = v.color_slope
        jpp_max[i] = v.jpp_max
        hpp_max[i] = v.hpp_max
        kpp_max[i] = v.kpp_max
            

        if (i > 30 and Test): 
            print i
            print "End of test"
            break

    Output.add_column('SOURCEID',sidarr)
    Output.add_column('Name',names)
    Output.add_column('RA', RA, unit='RADIANS')
    Output.add_column('DEC', DEC, unit='RADIANS')
    Output.add_column('N', N)
    Output.add_column('chip', chip)
    Output.add_column('one_chip', one_chip)

    Output.add_column('Stetson', Stetson)

    for b, band_name in zip(bands, band_names):
        bn = band_name + '_'
        Output.add_column(bn+'mean', b.mean)
#        print Output[bn+'mean'][0]
        Output.add_column(bn+'rms', b.rms)
        Output.add_column(bn+'min', b.min)
        Output.add_column(bn+'max', b.max)
        Output.add_column(bn+'peak_trough', b.peak_trough)

        Output.add_column(bn+'rchi2', b.rchi2)

        if rob:
            Output.add_column(bn+'meanr', b.meanr)
            Output.add_column(bn+'rmsr', b.rmsr)
            Output.add_column(bn+'minr', b.minr)
            Output.add_column(bn+'maxr', b.maxr)
            Output.add_column(bn+'peak_troughr', b.peak_troughr)

        if per:
            Output.add_column(bn+'lsp_per', b.lsp_per)
            Output.add_column(bn+'lsp_pow', b.lsp_pow)
            Output.add_column(bn+'fx2_per', b.fx2_per)

            
    Output.add_column('color_slope', color_slope)
    Output.add_column('jpp_max', jpp_max)
    Output.add_column('hpp_max', hpp_max)
    Output.add_column('kpp_max', kpp_max)

    Output.write(outfile, overwrite=True)
    print "Wrote output to %s" % outfile

    return

def spread_write_test (table, lookup) :
    """ Tests spreadsheet_write."""

    test_path = '/home/trice/reu/DATA/Merged_Catalogs/spreadsheet/test.fits'
    spreadsheet_write (table, lookup, -1, test_path, Test=True)
