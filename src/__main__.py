'''
Created on 19.08.2013

@author: tintinweb
@version: 1.3
'''
if __name__=='__main__':
    import modules.QA_Logger as QA_Logger
    LOG = QA_Logger.getLogger(name="argBrute")
    import modules.SimpleOptparse as SimpleOptparse
    from modules.AggroArgs import AggroArgs
    
    optDef = {  
            (('--help',     '-h'),              "This help"):                                   False,
            (('--verbosity',  '-v'),            "Enable verbose output"):                       QA_Logger.QA_Logger.L_INFO,
            (('--file-extensions',  '-f'),      "filter file extensions"):                      None,
            (('--blacklist','-b'),              "Filename blacklists"):                         "*.so,*.so.*",
            (('--params','-p'),                 "number of params to supply"):                  1,
            (('--param-length','-l'),           "max length of a param passed to executable"):  999,     
            (('--process-timeout','-t'),        "max alive time of a process in seconds"):      5,   
            (('--no-recursion', '-R'),          "no recursive file scanning"):                  False,   
            (('--modes', '-m'),                 "probe options (e.g. long,short,default)"):     "short,long,default",   
          }
    options,arguments=SimpleOptparse.parseOpts(optDef)
    LOG.setLevel(int(options['verbosity']))
        
    if not len(arguments):
        print SimpleOptparse.buildUsageString(optDef)
        exit()
        
    if options['file-extensions']:
        options['file-extensions']=options['file-extensions'].split(",")
        LOG.info("Scanning for file-extensions: %s"%options['file-extensions'])
    if options['blacklist']:
        options['blacklist']=options['blacklist'].split(",")
        LOG.info("Skipping blacklisted for files: %s"%options['blacklist'])
    if options['modes']:
        options['modes']=options['modes'].split(",")
        LOG.info("option probing modes enabled: %s"%options['modes'])
        
    # start the magic
    results = {}
    for path in arguments:
        b = AggroArgs(path,filter=options['file-extensions'], blacklist=options['blacklist'], recursive=not(options['no-recursion']))
        b.attack(params=int(options['params']), 
                 param_size=int(options['param-length']),
                 max_execution_time=int(options['process-timeout']),
                 modes=options['modes'])
        results[path]=b.hits[:]
    
    # end of magic
    print "\n\n===[Summary]==="
    for path,hits in results.iteritems():
        print "[*] Path: %s"%path
        nr = 0
        for h in hits:
            print "\n  [%s]---------------------------------------------------------"%nr
            print "     [ ] Path:      %s"%h.path
            print "     [ ] LogLines: \n                %s"%("\n                ".join(h.loglines))
            print "     [ ] Addr2Line: %s"%h.addr2line
            print "     [ ] EIP_Analysis: %s"%h.eip_analysis
            print "     [ ] Args:    \n                %s %s"%(h.path," ".join(["'%s'"%a for a in h.args]))

            nr +=1
        
    print LOG.getStats()