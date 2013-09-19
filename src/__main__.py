'''
Created on 19.08.2013

@author: tintinweb
@version: 1.3.2
'''
if __name__=='__main__':
    import modules.QA_Logger as QA_Logger
    LOG = QA_Logger.getLogger(name="argBrute")
    import modules.SimpleOptparse as SimpleOptparse
    from modules.AggroArgs import AggroArgs
    from modules.Scanner import Scanner
    from modules.Exploit import Exploit
    import os
    
    
    optDef = {  
            (('--help',         '-h'),     "This help"):                                   False,
            (('--verbosity',    '-v'),     "Enable verbose output"):                       QA_Logger.QA_Logger.L_INFO,
            (('--filter',       '-f'),     "filter filenames (e.g. qmail*)"):              None,
            (('--blacklist',    '-b'),     "Filename blacklists"):                         "*.so,*.so.*,dmesg,script,suspend,init,runlevel,reboot,shutdown,switchoff,*grep",
            (('--params',       '-p'),     "number of params to supply"):                  1,
            (('--param-length', '-l'),     "max length of a param passed to executable"):  999,     
            (('--process-timeout','-t'),   "max alive time of a process in seconds"):      5,   
            (('--no-recursion', '-R'),     "no recursive file scanning"):                  False,   
            (('--modes',        '-m'),     "probe options (e.g. long,short,default)"):     "short,long,default",   
            (('--output-poc',    '-o'),     "output directory for exploit PoC's "):         None, 
          }
    options,arguments=SimpleOptparse.parseOpts(optDef)
    LOG.setLevel(int(options['verbosity']))
        
    if not len(arguments):
        print SimpleOptparse.buildUsageString(optDef)
        exit()
        
    if options['filter']:
        options['filter']=options['filter'].split(",")
        LOG.info("Scanning with filter: %s"%options['filter'])
    if options['blacklist']:
        options['blacklist']=options['blacklist'].split(",")
        LOG.info("Skipping blacklisted files: %s"%options['blacklist'])
    if options['modes']:
        options['modes']=options['modes'].split(",")
        LOG.info("option probing modes enabled: %s"%options['modes'])
        
    # start the magic
    results = {}
    for path in arguments:
        scanner = Scanner(path,filter=options['filter'], blacklist=options['blacklist'], recursive=not(options['no-recursion']))
        
        # init aggro_args settings
        x = Exploit()           # general functionality
        x_aggro = AggroArgs()   # attack speciic stuff
        
        
        for nr,f in enumerate(scanner.walk()):

            # skip non-executable files
            if not (os.path.isfile(f) and os.access(f, os.X_OK)):
                LOG.debug("[>] Skipping - not executable - %s"%f)
                continue
            # skip non elf files
            if  os.name in ['posix','mac']:
                if not any(s in x.shellex("file '%s'"%f, shell=True).lower() for s in ['elf','executable']):
                    LOG.debug("[>] Skipping - File-Format mismatch - not ELF - %s"%f)
                    continue
            
            LOG.info( "[*] #%d - processing: %s"%(nr, f))
            
        
            x_aggro.attack( executable=f,
                            params=int(options['params']), 
                            param_size=int(options['param-length']),
                            max_execution_time=int(options['process-timeout']),
                            modes=options['modes'])
            
            results[path]=x_aggro.hits[:]
    
    # end of magic
    print "\n\n===[Summary]==="
    for path,hits in results.iteritems():
        print "[*] Path: %s"%path
        for nr,h in enumerate(hits):
            print "\n  [%s]---------------------------------------------------------"%nr
            print str(h)
            if options['output-poc']:
                with open("%s/%s_%s.py"%(options['output-poc'],str(nr),os.path.split(h.path)[-1]),'w') as f:
                    f.write(x_aggro.create_poc(h))
        
    print LOG.getStats()