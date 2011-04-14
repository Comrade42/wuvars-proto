''' A one-time script to make a stats table (no period information) from 
my WSERV more-or-less complete catalog! it should probably run overnight.'''

import atpy
import filter as ft
from datetime import datetime
import spreadsheet

path = '/media/storage/Documents/Research/reu/DATA/Merged_Catalogs/'

w = atpy.Table(path+'wserv_errbits_combined_err_lt_0.15.fits')
c = atpy.Table(path+'stat/the_REAL_corrections_table.fits')

print "loaded stuff at " + datetime.now().strftime("%a, %d %b %Y %H:%M:%S")


w_clipped = ft.happy_chipnights( w, c )

del w

print "clipped stuff at " + datetime.now().strftime("%a, %d %b %Y %H:%M:%S")

w_clipped.write(path + 'wserv_happy.fits')

print "saved stuff at " + datetime.now().strftime("%a, %d %b %Y %H:%M:%S")

mock_lookup = spreadsheet.base_lookup(w_clipped)

print "mock lookup at " + datetime.now().strftime("%a, %d %b %Y %H:%M:%S")

global_stats = spreadsheet.spreadsheet_write ( w_clipped, mock_lookup, 0, 
                                               path+"global_stats1.fits")

print "made stats at " + datetime.now().strftime("%a, %d %b %Y %H:%M:%S")+"!!!"


