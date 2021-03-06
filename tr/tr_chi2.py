''' Functions that interface with Palmer's runchi2 program.

Don't use this one.
'''

print "You're using the DEPRECATED version of chi2! Use the other one!"
# Don't use this one.

# Current major issues: This code does not recognize error messages given by 
# runchi2! If something goes wrong everything crashes and burns. 

import subprocess
import numpy
import tr_plot

def chi_input_writer (name, t, x, err, outfile):
    ''' Writes data to a table suitable for runchi2's input. Returns outfile.'''

    if not (t.size == x.size == err.size):
        print "Input arrays must be the same size!"
        return None

    f = open(outfile,'w')
    f.write(name+"\n")
    f.write(str(t.size)+"\n") #small possibility i should add or sub 1 to this
    
    for i in range(t.size):
        f.write("%f \t %f \t %f \n" % (t[i], x[i], err[i]))

    f.close()

    return outfile


def smart_chi_writer (table, sid, band = 'j') :
    '''Writes one source's data into runchi2's format.'''

    print band

    name = "." + band + str(sid)
    w = numpy.where(table.SOURCEID == sid) # I may alter this line to filter error 
                                     # bits and such

    if 'm' in band:
        tail = "PNT"
    else:
        tail = "APERMAG3"

    t = table.MEANMJDOBS[w]
    x = table.data[band.upper()+tail][w]
    err=table.data[band.upper()+tail+"ERR"][w]

    # do i want to use a data path for the outfile? ... yes

    outfile = '/home/trice/reu/DATA/chi2/' + name
    return chi_input_writer (name, t, x, err, outfile) 

def run_chi (infile) :
    ''' Runs Palmer's runchi2 program on a given input file. 
    '''
    # This function, as yet incomplete, will probably make heavy use of the 
    # "subprocess" module. With any luck I can pass the output of
    # runchi2 to stdout, have python's subprocess call return that stdout 
    # string, and then parse the string from there, and thus return
    # a tuple or _dictionary_ of important values such as periods.
    
    #let's figure out what's needed here.

    args = ["runchi2","3","12","-i",infile]

    runchi = subprocess.Popen(args, stdout=subprocess.PIPE)

    result = runchi.communicate()[0]
    #print result
    return result


def parse_chi (string) :
    ''' Parses the output of runchi2 for one source, returns frequency '''
    # maybe it would be a better idea to define this earlier and have
    # run_chi call this function before returning. The big sloppy string is
    # never ever useful until it's been parsed...


    # Okay, we're gonna have to do some stripping and some parsing (splitting)

    # The following assumes that the data is on the second-to-last line
    # (the last line is el blanco) ... (I mean blank)
    results = string.split('\n')[-2].split('\t')

    print results
    
    name = results[0]
    fbest= float(results[1])

    return fbest
    
def chi_analyze (table, sid, band = 'j') :
    ''' Does everything for one source and returns the frequency information.'''

    datafile = smart_chi_writer(table,sid,band)
    
    return parse_chi ( run_chi ( datafile ) )

def test_analyze (t, x, err):
    ''' Takes in test data, returns best frequency '''

    datafile = chi_input_writer("test", t, x, err, 
                                '/home/trice/reu/DATA/chi2/chitest.in')

    return parse_chi ( run_chi ( datafile ) )

def chi_plot (table, sid, band = 'j', harmonic=1) :
    ''' Does everything for one source and plots a phase plot.'''

    f = chi_analyze (table, sid, band)

    period = 1./f
    
    tr_plot.plot_phase (table, sid, period*harmonic, band)

    return period
    
# Next step... combine stat and chi2 to make a table of best-freq and chi^2 
# values for every source. I've been assuming that chi^2 can be used as a 
# measure of how good the periodicity actually is.

def chi_stat #uh, gonna make this better
