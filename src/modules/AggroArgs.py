#! /usr/bin/env python
# vim:ts=4:sw=4:expandtab
"""
Created on 19.08.2013

@author: tintinweb
"""
import modules.QA_Logger as QA_Logger
LOG = QA_Logger.getLogger(name="argBrute")
from Exploit import Exploit
from UsageParser import UsageParser

import os, re

try:
    any([])
except:
    # for python 2.4 - redefine any
    def any(list):
        for i in list:
            if i==True: return True
        return False

class Hit(object):
    """Hit Container"""
    def __init__(self,path,args, loglines,addr2line,eip_analysis):
        self.path=path
        self.args=args
        self.loglines=loglines
        self.addr2line=addr2line
        self.eip_analysis = eip_analysis
        
    def import_dict(self,d):
        """set merge dict to class params"""
        assert (isinstance(d,dict))
        for k,v in d:
            setattr(self,k,v)
            
    def  __str__(self):
        info = "  [x] Target:      %s"%self.path
        info += "\n     [ ] LogLines: \n                %s"%("\n                ".join(self.loglines))
        info += "\n     [ ] Addr2Line: %s"%self.addr2line
        info += "\n     [ ] EIP_Analysis: %s"%self.eip_analysis
        info += "\n     [ ] Args:    \n                %s %s"%(self.path, " ".join(["'%s'"%a for a in self.args])  )
        return info
            

class AggroArgs(object):
    """AggroArgs Attack"""
    def __init__(self):
        """init"""
        self.cache = {}
        self.hits = []
        self.exploit = Exploit()
        # set buffer overflow detection output to be written to stderr
        os.environ['LIBC_FATAL_STDERR_']='1'
        
    def __del__(self):
        """cleanup env vars set in init"""
        del(os.environ['LIBC_FATAL_STDERR_'])
        
        
    def _addr2line(self,executable, dmesg_line):
        """resolve addr2line"""
        #[2178587.552851] xxxx[8562]: segfault at 2 ip 0000000000000002 sp 00000000ffbd2ce4 error 14
        c_segf = re.compile(r"ip ([\da-fA-F]+) sp ([\da-fA-F]+)",)
        m = c_segf.search(dmesg_line)
        ret = []
        if m:
            ip,sp = m.groups()
            
            ret.append(self.exploit.shellex("addr2line -e %s %s"%(executable,ip),shell=True).strip())
            ret.append(self.exploit.shellex("addr2line -e %s %s"%(executable,sp),shell=True).strip())
            
        return ret
    
    def _eip_to_pattern_location(self,dmesg_line):
        """get overflow offset"""
        #[2178587.552851] xxxx[8562]: segfault at 2 ip 0000000000000002 sp 00000000ffbd2ce4 error 14
        c_segf = re.compile(r"at ([\da-fA-F]+) ip ([\da-fA-F]+) sp ([\da-fA-F]+)",)
        m = c_segf.search(dmesg_line)
        ret = {}
        if m:
            at,ip,sp = m.groups()
            ret['at']=at
            ret['ip']=ip
            ret['sp']=sp
            try:
                ret['eip_ascii']=at.decode('hex')
                ret['eip_ascii_real']=ret['eip_ascii'][::-1]
                ret['eip_offset']=self.exploit.createPatternCyclic(9999).index(ret['eip_ascii_real'])
            except ValueError, ve:
                pass
            except TypeError, te:
                pass
        return ret
        
    def _prepare_args(self,p,params,param_size, mode=None):
        """generate args"""
        
        '''  -- disable caching
        cache = self.cache.get('prepare_args',{})
        if cache.has_key(p):
            return cache[p]
        '''
        
        usage = self.exploit.shellex("%s --help -h"%p, shell=True, max_execution_time=1) 
        
        # parse args for cmdline switches
        # prepare args array
        # long: \s--[a-zA-Z0-9]+
        # short: \s-[a-zA-Z0-9]+
        # legacy stuff
        args=[]
        if mode in "brute":
            yield [self.exploit.createPatternCyclic(param_size) for x in range(params)]
            
        elif mode in ("short","long"):
            m = None
            if 'short' in mode:
                m = re.findall(r"[\[\s](-[a-zA-Z0-9]+)",usage)
                if not m: raise Exception("option probing failed")
            elif 'long' in mode:
                m = re.findall(r"[\[\s](--[a-zA-Z0-9_-]+)",usage)
                if not m: raise Exception("option probing failed")  
    
            if m:
                m = [x.strip() for x in m]
                if '-h' in m: m.remove("-h")
                if '--help' in m: m.remove("--help")
                for a in m:
                    # append -switch, param, -switch,param
                    a=a.strip()
                    if 'short' in mode:
                        #append option, value
                        args.append(a)
                        args.append(self.exploit.createPatternCyclic(param_size))
                    else:
                        #append option=value
                        args.append("%s=%s"%(a,self.exploit.createPatternCyclic(param_size)))                
                # for legacy
                yield args
        elif "smart-" in mode:
            # UsageParser NG
            up = UsageParser(appname=p, intext=usage)
            argchain = up._build_argchain()                 # populates observed_options
            if "smart-sequence" in mode:
                for chain in argchain:
                    yield self._interpret_argchain(chain, long=True, param_size=param_size)        # yield shortform
                    yield self._interpret_argchain(chain, long=False, param_size=param_size)       # yield longform
                
            elif "smart-short":
                #create chains like:  -i -a -if <CYCLPATTERN> ...
                len(argchain)       # populate observed_options
                for o in (oo for oo in up.observed_options if oo.islong==False):
                    args.append(str(o))
                    if o.requires_value:
                        args.append( self.exploit.createPatternCyclic(param_size))
                yield args
            elif "smart-long":
                 #create chains like:  --interval --aoption --interface=<CYCLPATTERN> ...
                len(argchain)       # populate observed_options
                for o in (oo for oo in up.observed_options if oo.islong==True):
                    if o.requires_value:
                        args.append( "%s=%s"%(str(o),self.exploit.createPatternCyclic(param_size)))
                yield args
            # get all long options

        ''' disable caching
        self.cache['prepare_args']={}
        self.cache['prepare_args'][p]=args
        '''
                
    def _interpret_argchain(self, chain, param_size, long=None):
        res = []
        for o in chain:
            if  o.typ=="TOptional":
                # skip TOptional for now.. just deref it
                res += self._interpret_argchain(o.e, long=long, param_size=param_size)
            elif o.typ=="TVar":
                # replace with cyclic pattern
                res.append(self.exploit.createPatternCyclic(param_size))
            elif o.typ=="TOpt":
                if long and not o.islong==long:
                    # skip unrelated ones
                    continue
                res.append(str(o))
            '''
            else:
                raise Exception("ERROR")
            '''
        return res    
        
           
    def attack(self, executable, params=1, param_size=999,max_execution_time=10,modes=['short','long','default','brute','smart-long','smart-short']):
        """attack single file"""
        # get initial log messages
        last_log = self.exploit.check_log()
                
        for mode in modes:
            # get logdiff
            
            try:
                argchains = self._prepare_args(executable,params,param_size,mode=mode)
            except:
                # options unparseable, 
                LOG.debug("  [x] unparseable %s options - skipping"%(mode))
                continue
            
            for args in argchains:
                txt_args=[]
                for a in args:
                    if len(a)>25:
                        txt_args.append("%s.."%a[:25])
                    else:
                        txt_args.append(a)
                LOG.debug("  [ ] probing args: (items truncated) %s"%txt_args)
                # execute target
                last_log = self.exploit.check_log()
                ret = self.exploit.shellex(cmd=executable, args=args, max_execution_time=max_execution_time) 
                last_log = self.exploit.check_log(compare_with=last_log)
                #handle buffer overflow caught by stack guard
                if any(s in ret.lower() for s in ['terminated','overflow','backtrace','memory map']):
                    last_log.append(ret)
                    LOG.warning("  [!] Buffer overflow caught by stack_guard - %s"%executable)
                    
                if len(last_log):
                    LOG.FAIL( "  [!] LogCheck failed! - %s (%s)"%(executable,mode))
                    
                    debug_args = ["'%s'"%a for a in args]
                    LOG.debug("  [ ] Cmdline: %s %s"%(executable," ".join(debug_args)))
                    a2lines = []
                    eiplines = []
                    for l in last_log:
                        LOG.warning("     %s"%l)
                        a2line = self._addr2line(executable,l)
                        a2lines.append(a2line)
                        LOG.warning("  [ ]     Addr2Line: %s"%repr(a2line))#
                        eipline = self._eip_to_pattern_location(l)
                        eiplines.append(eipline)
                        LOG.warning("  [ ]     EIP_analysis: %s"%repr(eipline))
                        
                        
                    self.hits.append(Hit(path=executable,
                                         args=args,
                                         loglines=last_log,
                                         addr2line=a2lines,
                                         eip_analysis=eiplines))
                        
                        
                else:
                    LOG.PASS("  [*] %s (%s) "%(executable,mode))
                
                
    def create_poc(self, hit):
        template = """#! /usr/bin/env python
# vim:ts=4:sw=4:expandtab
'''Created on %s

@author:  aggroArgs /
@contact: https://github.com/tintinweb/aggroArgs
---------------------------------------------
Outline (max 350 chars): 

%s
---------------------------------------------
'''
import subprocess

CMD = %s
ARGS = %s

if __name__=='__main__':
    print "Target: %%s"%%CMD
    print "[ ] executing, please stand by ..."
    ret = subprocess.Popen([CMD]+ARGS, shell=False,stdout=subprocess.PIPE,stderr=subprocess.STDOUT) 
    print "[*] done!"
"""
        import time
        localtime=time.asctime( time.localtime(time.time()) )
        return template%(localtime,str(hit)[:350],repr(hit.path),repr(hit.args))


if __name__=='__main__':
    print "WARNING!! -- AggroArgs.__main__ - deprecated - use __main__.py instead - only __main__.py will be maintained!"
    LOG = QA_Logger.getLogger(name="argBrute")
    import SimpleOptparse as SimpleOptparse
    from Scanner import Scanner

    
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
            (('--output-poc',   '-o'),     "output directory for exploit PoC's "):         None,   
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
                if not any(s in x.shellex("file -L '%s'"%f, shell=True).lower() for s in ['elf','executable']):
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