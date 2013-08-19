'''
Created on 21.11.2011
@author: tintinweb
'''
import getopt,sys,os

class unique_class(object):
    '''
    dummy class to create unique objects as options for this class
    '''
    identification = None
    def __init__(self,identification):
        '''
        @param identification: just a identification for this new class 
        '''
        self.identification=identification
        
MANDATORY=unique_class('OPTION_MANDATORY')          #flag that marks mandatory options (because we dont want to use None for that)
__INDICATOR_FLAG=False                              #this indicates that the configured option is a flag and does not expect a value
FMT_Helpline="\n  %-11s %-30s %-s."
FMT_Helpline_with_default=(FMT_Helpline+"\n"+45*' '+"*** %s")

def arrangeArgTuple(argTuple, longFirst=True):
    '''
    sort tuple according to longFirst
    @param longFirst: True,  sort like (--long-opt, -short)
    @param longFirst: False, sort like (-short, --long-opt)
    @param argTuple: must be of type tuple
    @return: sorted tuple
    '''
    assert type(argTuple) is tuple, "invalid type for param 'argTuple' - cant extract name"
    #assert(type(argTuple[0]) is str)
    #assert(type(argTuple[1]) is str)
    
    if longFirst==True:
        #long form first (--)
        if argTuple[0][:2]=="--":
            #first item is long form, return it
            return argTuple
        else:
            #2nd item is long form, switch it
            return (argTuple[1],argTuple[0])
    else:
        #short form first (-)
        if argTuple[1][:2]=="--":
            #2nd item is long form, this means 1st is short, return it
            return argTuple
        else:
            #first item is long form, 2nd is short, switch it
            return (argTuple[1],argTuple[0])
            
def getArgName(argTuple,longName=True):
    '''
    extract option name from tuple (long-name)
    @param longName: True,  return name of --long-name
    @param longName: False, return name of -short
    @param argTuple: must be of type tuple
    @return: tuple-option name
    '''
    assert type(argTuple) is tuple, "invalid type for param 'argTuple' - cant extract name"
    argTuple = arrangeArgTuple(argTuple)
    if longName==True:
        return str(argTuple[0])[2:]
    else:
        return str(argTuple[1])[1:]
    
def buildUsageString(opt_def, message="", fmt=FMT_Helpline, fmt_helpline_with_default=FMT_Helpline_with_default):
    '''
    generate the usage string for the option_parser configuration 
    @param opt_def: dictionary with option configuration valid for this application
    @return: usage string
    '''
    strHelpMessage = "%s\n"%(message)
    strHelpUsageMandatory = ""      #will be build later
    strHelp = "\nMandatory arguments to long options are mandatory for short options too.\n"
    #arrange short option first
    
    # cycle through function arguments
    for helpline,defValue in opt_def.iteritems():
        # this level: ((--timeout,-t):default_val)  as dictionary
        optionTuple=arrangeArgTuple(helpline[0],False)
        # create string for defualtvalue
        # init
        if defValue==__INDICATOR_FLAG:
            strHelp +=fmt%(optionTuple[0]+",",optionTuple[1],helpline[1]) 
        elif defValue==MANDATORY:
            strHelp +=fmt%(optionTuple[0]+",",optionTuple[1],helpline[1])
            strHelpUsageMandatory +="%-s=<value> "%(optionTuple[1])  #add mandatory long val to usage line
        else:
            defaultStr = "DEFAULT='%s'"%(defValue)
            helpstrmultiline= ("\n"+45*" ").join(chunk_string(helpline[1],60))
            strHelp +=fmt_helpline_with_default%(optionTuple[0]+" <value>,",optionTuple[1]+"=<value>",helpstrmultiline,defaultStr)            
       
    strHelpUsage = "\nUsage: %s %s [OPTIONS] [Argument(s) ...]\n"%(os.path.basename(sys.argv[0]),strHelpUsageMandatory)
    #get the def tuples and print the line with the corresponding text
    return strHelpMessage+strHelpUsage+strHelp+"\n"

def chunk_string(s, chunk_size):
    retn=[]
    
    for start in range(0,len(s),chunk_size):
        curr = s[start:start+chunk_size]
        retn.append(curr)
    return retn


def parseOpts(opt_def):
    '''
    parse options from argv to the configured options dictionary
    @param opt_def: dictionary with option configuration valid for this application
    @return: tuple (options,args). dictionary of parsed options and a list of optional arguments
    '''
    # we want something like this
    #     optDef = {  
    #            (('--help','-h'),"This help"):"this is the help you need",
    #            (('--verbosity','-v'),"Enable verbose output"):True,
    #            (('--timeout','-t'),"Timeout the console stays open"):5,
    #            (('--branch','-b'),"use this branch"):'1.1'            
    #          }

    # dOpts holds all default values and is the returnarray of our function
    #
    #  dOpts= { 'timeout' : 5,
    #           'branch'  : '1.1',
    #             .... 
    #           }     
    #
    # init
    dOpts={}                #default values for options (returnarray)
    lstOpts=[]              #GETOPT option list for long options 
    strOpts=""              #GETOPT option string for short options
    lstOptsTuples=[]        #list of option tuples [  (short,long), (short,long) ] to compare against
    
   
    ''' ---- PHASE 1 ---- generate options for getopt from opt_def dictionary '''
    
    # cycle through function arguments
    for defline,defValue in opt_def.iteritems():
        # this level: ((--timeout,-t):default_val)  as dictionary
        #parent_name=None                                    #init last line
        #for paramline in defline:
        # this level: (--timeout, -t)  tuple  or   default value as str
        
        #print len(paramline)
        #if len(paramline)==2   its a --long -short tuple
        #if len(paramline)>=2   its a string
        
        assert type(defline) is tuple, "SimpleOptparser: invalid type for 'defline' - check config: line must be like this: ((--help, -h),this is the helptext for this option)"
        paramline=defline[0]
        assert type(paramline) is tuple, "SimpleOptparser: invalid type for 'paramline' - check config: line must be like this: (--help, -h)"
        # tuple: (--timeout,-t)
        # grab the longer string and use it as option dictionary return value
        #print "argLong,argShort "+str(paramline)
        
        ##FIXME: filter  -h --help 
        paramline=arrangeArgTuple(paramline)            #arrange long option first
        # IF defaultValue is None then treat this as FLAG and not as Option with value
        # init key value pairs
        strLongOpt=str(paramline[0])[2:]
        strShortOpt=str(paramline[1])[1:]
        
        # check if this option expects a flag(FALSE) or some value (<>FALSE)
        if not defValue==__INDICATOR_FLAG:
            # we have key value paris
            strLongOpt+="="
            strShortOpt+=":"
            
            
        lstOpts.append(strLongOpt)                      #save long option to long option list without leading - but with trailing =
        strOpts+=strShortOpt                            #concat short option to optionstring without leading -
        
        parent_name=getArgName(paramline)
        lstOptsTuples.append(paramline)


        
        dOpts[str(parent_name)]=defValue
    
    #print "dopts defaults  "+str(dOpts)
    #print "lopts longlist  "+str(lstOpts)
    #print "strOpts shortlist  "+str(strOpts)
    #print "strOptsUsage helptext  "+str(lstOptsUsage)
    #print buildUsageString(lstOptsUsage)
    
    ''' ---- PHASE 2 ----  parse options using getopt '''
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], strOpts, lstOpts)
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        print buildUsageString(opt_def)
        sys.exit(2)

    #print "parse options"
    #parse option tuples from config =
 
     
    lstMandatoryOptionsHit=[]        #contains all mandatory options that where hit
    lstMandatoryOptionsMissing=[]    #contains all missing mandatory options
    for o, a in opts:
        option_hitcount=0
        if o in ('-h','--help'):
            print buildUsageString(opt_def)
            sys.exit()
        else:
            for chkTuple in lstOptsTuples:
                #print o
                #print chkTuple
                
                if o in chkTuple: 
                    #print "hit"
                    if dOpts[str(getArgName(chkTuple))]==__INDICATOR_FLAG:
                        a=True       #toggle flag to true
                    #handle mandatory options - add them to a hitlist for later comparison
                    if dOpts[str(getArgName(chkTuple))]==MANDATORY:
                        if chkTuple not in lstMandatoryOptionsHit:
                            #only add once
                            lstMandatoryOptionsHit.append(chkTuple)  #mark option as hit!
                    #now overwrite the default value :)
                    dOpts[str(getArgName(chkTuple))]=a               #assign the value
                    option_hitcount+=1                               #random stats
                else:
                    #no hit, check if this option was mandatory!
                    if dOpts[str(getArgName(chkTuple))]==MANDATORY:
                        if chkTuple not in lstMandatoryOptionsMissing:
                            #only add it if its not already there to avoid dupes
                            lstMandatoryOptionsMissing.append(chkTuple)                    
        assert (option_hitcount==1), "unhandled option - option was not hit or hit multiple times: %s"%(option_hitcount)
        #assert False, "unhandled option"
    # ...
    ''' check the mandatory list '''
    # strip otions from hitlist in options missing list
    lstMandatoryOptionsMissing= [val for val in lstMandatoryOptionsMissing if val not in lstMandatoryOptionsHit]

    
    
    ''' ---- PHASE 3 ---- cleanup and stuff '''

    if len(lstMandatoryOptionsMissing)>0:
        strMissingOptions=""
        for lstItem in lstMandatoryOptionsMissing: strMissingOptions+= "\t%s\n"%(str(lstItem))
        print buildUsageString(opt_def,message="-- missing mandatory option(s) --\n\nThe following options are mandatory:\n%s"%(strMissingOptions))
        sys.exit()
    #print "options hit: %s"%(overall_option_hitcount)
    
    ''' ---- PHASE 4 ---- check if there are still mandatory options to fill '''
    # in case there were no opts/args passed via cmdline
    strMissingOptions=""
    for key,val in dOpts.iteritems():
        if val==MANDATORY:
            strMissingOptions+= "\t--%s\n"%(str(key))
        #there are still mandatory fields left! report this
    if len(strMissingOptions)>0:
        print buildUsageString(opt_def,message="-- missing mandatory option(s) --\n\nThe following options are mandatory:\n%s"%(strMissingOptions))
        sys.exit()


    return (dOpts,args)

'''

#import the option parser do unleash its magic
import SimpleOptparse


import SimpleOptparse

if __name__ == '__main__':
    # define the options we want to catch on the commandline
    # Format:
    #     ((long_option,short_option), a short helpline for this option): default value
    #
    optDef = {  
                (('--help',     '-h')       ,"This help"):                                False,
                (('--verbose',  '-v')       ,"Enable verbose output"):                    False,
                (('--timeout',  '-t')       ,"Timeout for the console to stay open"):         5,
                (('--branch',   '-b')       ,"use specific branch   "):                   '1.1',
                (('--magic' ,   '-m')       ,"insert random magic values here"):           None,
                (('--deluxe',   '-d')       ,"Deluxe Option cost more than a million"):   False,
                (('--cant-afford','-c')     ,"sure you cant! ha ha ha"):                  False,    
                (('--manD',     '1')        ,"This is a mandatory option!"):              SimpleOptparse.MANDATORY,     
              }
    # do the magic
    options,arguments= SimpleOptparse.parseOpts(optDef)
    # if no option was hit it will print the usage/help & exit
    # if options were hit, it returns a tuple in the following format:
    #
    # ( {dictionary of all parsed options}, [a list of optional arguments])
    print options
    print arguments
'''
