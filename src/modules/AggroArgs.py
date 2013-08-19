#! /usr/bin/env python
# vim:ts=4:sw=4:expandtab
'''
Created on 19.08.2013

@author: mortner
'''

import modules.QA_Logger as QA_Logger
LOG = QA_Logger.getLogger(name="argBrute")

import subprocess, os,fnmatch, time, signal, re

try:
    any([])
except:
    # for python 2.4 - redefine any
    def any(list):
        for i in list:
            if i==True: return True
        return False

class Hit(object):
    def __init__(self,path,args, loglines,addr2line):
        self.path=path
        self.args=args
        self.loglines=loglines
        self.addr2line=addr2line
        
        # set buffer overflow detection output to be written to stderr
        os.environ['LIBC_FATAL_STDERR_']='1'


class AggroArgs(object):
    def __init__(self, path, filter=None,blacklist=None, recursive=True):
        self.path = path
        self.filter = filter
        self.recursive= recursive
        self.blacklist = blacklist
        
        self.hits = []
        
    def _shell(self,cmd,args=[], shell=False, max_execution_time=10):
        if isinstance(cmd,basestring):
            cmd=[cmd]
        
        out = ""
        try:
            
            ret = subprocess.Popen(cmd+args, shell=shell,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)  
            self.wait_timeout(ret,max_execution_time)
            
            if not ret:
                raise "Exception - returned false"
            out, _ = ret.communicate()
            
        except RuntimeError, er:
            LOG.info( "Timeout - %s" %" ".join(cmd))
            os.kill(ret.pid,signal.SIGTERM)
            
        except Exception, e:
            LOG.exception("%s - (cmd=%s, args=%s, shell=%s, exec_time=%s"%(e,cmd,args,shell,max_execution_time))

        return out
    
    def wait_timeout(self,proc, seconds):
        """Wait for a process to finish, or raise exception after timeout"""
        start = time.time()
        end = start + seconds
        interval = min(seconds / 1000.0, .25)
    
        while True:
            result = proc.poll()
            if result is not None:
                return result
            if time.time() >= end:
                raise RuntimeError("Process timed out")
            time.sleep(interval)
    
    def _check_log(self,compare_with=None):
        '''
        differential dmesg check
        '''
        filter = ['gfault','error']
        entries = self._shell(cmd="/bin/dmesg | egrep -i '(%s)'"%"|".join(filter),shell=True)
        
        entries = entries.split("\n")
        output = []
        if compare_with:
            for line in entries:
                if line not in compare_with:
                    output.append(line)
        else: 
            output = entries
        return output
    
    def badchars(self,skip=[]):
        return "".join([chr(i) for i in range(256) if not i in skip])    

    def createPatternCyclic(self,size):
        char1="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        char2="abcdefghijklmnopqrstuvwxyz"
        char3="0123456789"
        
        charcnt=0
        pattern=""
        max=int(size)
        while charcnt < max:
            for ch1 in char1:
                for ch2 in char2:
                    for ch3 in char3:
                        if charcnt<max:
                            pattern=pattern+ch1
                            charcnt=charcnt+1
                        if charcnt<max:
                            pattern=pattern+ch2
                            charcnt=charcnt+1
                        if charcnt<max:
                            pattern=pattern+ch3
                            charcnt=charcnt+1
        return pattern 
    
    def walk_dir(self,path=None, filter=None, blacklist=None, recursive=None):
        path = path or self.path
        filter = filter or self.filter
        recursive = recursive or self.recursive
        blacklist = blacklist or self.blacklist
        
        if isinstance(filter, basestring):
            filter=[filter]
        
        for root, dirnames, filenames in os.walk(path):
            if filter:
                filtered_files = []
                for f in filter:
                    filtered_files+=fnmatch.filter(filenames,f)
                filenames = set(filtered_files)
                
            # filter blacklist
            if blacklist:
                filtered_files = []
                for b in blacklist:
                    filtered_files+=fnmatch.filter(filenames,b)
                
                # now remove all paths in filenames that are in filtered_files
                filenames = [f for f in filenames if f not in filtered_files]
                    
            
            for filename in filenames:
                yield os.path.join(root,filename)
            if not recursive:
                break
                
        
    def _addr2line(self,executable, dmesg_line):
        #[2178587.552851] libsmphibsplugi[8562]: segfault at 2 ip 0000000000000002 sp 00000000ffbd2ce4 error 14
        c_segf = re.compile(r"ip ([\da-fA-F]+) sp ([\da-fA-F]+)",)
        m = c_segf.search(dmesg_line)
        ret = []
        if m:
            ip,sp = m.groups()
            
            ret.append(self._shell("addr2line -e %s %s"%(executable,ip),shell=True))
            ret.append(self._shell("addr2line -e %s %s"%(executable,sp),shell=True))
            
        return ret
        
    def _prepare_args(self,p,params,param_size, mode=None):
        
        usage = self._shell("%s --help -h"%p, shell=True, max_execution_time=1) 
        # parse args for cmdline switches
        # prepare args array
        # long: \s--[a-zA-Z0-9]+
        # short: \s-[a-zA-Z0-9]+
        m = None
        if 'short' in mode:
            m = re.findall(r"(\s-[a-zA-Z0-9]+)",usage)
        elif 'long' in mode:
            m = re.findall(r"(\s--[a-zA-Z0-9]+)",usage)

        if m:
            if '-h' in m: m.remove("-h")
            if '--help' in m: m.remove("--help")
            args = []
            for a in m:
                # append -switch, param, -switch,param
                a=a.strip()
                if 'short' in mode:
                    #append option, value
                    args.append(a)
                    args.append(self.createPatternCyclic(param_size))
                else:
                    #append option=value
                    args.append("%s=%s"%(a,self.createPatternCyclic(param_size)))
        else:
            args = [self.createPatternCyclic(param_size) for x in range(params)]
        
        return args
        
                        
                
    def attack(self, params=1, param_size=999,max_execution_time=10,modes=['short','long','default']):
        # get initial log messages
        last_log = self._check_log()
        
        nr = 0
        for p in self.walk_dir():
            # check if executable
            if not (os.path.isfile(p) and os.access(p, os.X_OK)):
                continue
            if not "elf" in self._shell("file '%s'"%p, shell=True).lower():
                LOG.debug("Skipping - NOT in ELF file format - %s"%p)
                continue
            
            LOG.debug( "#%d - processing: %s"%(nr, p))
            nr +=1
            
            for mode in modes:
            
                # get new log messages since last logcheck
                last_log = self._check_log()
                args = self._prepare_args(p,params,param_size,mode=mode)
                ret = self._shell(cmd=p, args=args, max_execution_time=max_execution_time) 
                last_log = self._check_log(compare_with=last_log)
                #handle buffer overflow caught by stack guard
                if any(s in ret.lower() for s in ['terminated','overflow','backtrace','memory map']):
                    last_log.append(ret)
                    LOG.warning("Buffer overflow caught by stack_guard - %s"%p)
                    
                if len(last_log):
                    LOG.FAIL( "#%d - new log entries detected! - %s"%(nr,p))
                    
                    debug_args = ["'%s'"%a for a in args]
                    LOG.debug("Cmdline: %s %s"%(p," ".join(debug_args)))
                    a2lines = []
                    for l in last_log:
                        LOG.warning("     %s"%l)
                        a2line = self._addr2line(p,l)
                        a2lines.append(a2line)
                        LOG.warning("     Addr2Line: %s"%repr(a2line))#
                        
                    self.hits.append(Hit(path=p,args=args,loglines=last_log,addr2line=a2lines))
                        
                        
                else:
                    LOG.PASS("#%d - %s"%(nr,p))
    
if __name__=='__main__':
    import modules.SimpleOptparse as SimpleOptparse
    
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
            print "     [ ] Args:    \n                %s %s"%(h.path," ".join(["'%s'"%a for a in h.args]))

            nr +=1
        
    print LOG.getStats()