'''
Created on Dec 22, 2011

@author: mortner



CHANGELOG:
    + initial logging facility for QA
    + added colors
    + migrated testrun-facility into logger
    + added stats for all loglevels [missing] 

'''
import logging

def getLogger(**kwargs):
    '''for now we'll only allow keywordargs
    
        if logger exists, it will be returned
        if keyword "force" exists, logging instance will be re-initialized, 
    '''
    if not kwargs.has_key('name'): kwargs['name']=QA_Logger.defaultNAME
    
    # check if logging instance already exists, if so, return it and use it, this makes life much easier
    if  kwargs['name'] in logging.getLogger().manager.loggerDict.keys():
        log =  logging.getLogger( kwargs['name'])
        if kwargs.has_key('force'):
            log._setDefaults(**kwargs)          #override defaults with new ones? only if kwargs[force] is set?
        return log
    
    # create new logging instance
    logging.setLoggerClass(QA_Logger)
    log = logging.getLogger( kwargs['name'])
    log._setDefaults(**kwargs)
    log._reinit()
    return log

    
    

class Color:
    class Palette:
        '''
        dummy, as python 2.5 does not support namedtuples
        '''
        black = None
        red = None
        green = None
        yellow = None
        blue = None
        purple = None
        cyan = None
        grey = None
    #forcolor
    endc =  "\033[0m"
    black = "\033[30m"
    red =   "\033[31m"
    green = "\033[32m"
    yellow ="\033[33m"
    blue =  "\033[34m"
    purple ="\033[35m"
    cyan =  "\033[36m"
    grey =  "\033[37m"
    
    #back color
    background = Palette
    background.black =  "\033[40m"
    background.red =    "\033[41m"
    background.green =  "\033[42m"
    background.yellow = "\033[43m"
    background.blue =   "\033[44m"
    background.purple = "\033[45m"
    background.cyan =   "\033[46m"
    background.grey =   "\033[47m"    

    #attribs
    bold =      "\033[1m"
    underline = "\033[4m"
    blink =     "\033[5m"
    invert =    "\033[7m"
    
class NoLogging(logging.Logger):
    
    def __init__(self, name):
        logging.Logger.__init__(self, name)   
        self.propagate=False

class QA_Logger(logging.Logger): 
    defaultFORMAT= "[%(asctime)s] %(levelname)s - %(message)s "
    #defaultFORMAT="%(asctime)s [%(funcName)s: %(filename)s,%(lineno)d] %(message)s"
    #defaultFORMAT = "[%(asctime)s] %(levelname)s - %(name)s :: %(module)s:%(lineno)d %(funcName)s - %(message)s "
    defaultLOGLEVEL = logging.INFO
    defaultNAME="QA_Default"#default logger name
    defaultNAME=__name__
    
    
    # ------------ just to know they are here
    qaFORMAT=None
    qaLOGLEVEL=None
    qaNAME=None
    qaLOGFILE=None
    qaLOGFILE_LEVEL=None
    
                            #wrap loglebels
    L_DEBUG=logging.DEBUG
    L_INFO=logging.INFO
    L_WARNING=logging.WARNING
    L_ERROR = logging.ERROR
    L_CRITICAL=logging.CRITICAL
    L_FAIL = logging.ERROR -1    #use FAIL/PASS as loglevels
    L_PASS = logging.INFO + 1
    L_SUCCESS = logging.INFO + 2
    
    #map Loglevels to Name
    LL_to_Name = { L_DEBUG:     'DEBUG   ',
                   L_INFO:      'INFO    ',
                   L_WARNING:   'WARNING ',
                   L_ERROR:     'ERROR   ',
                   L_CRITICAL:  'CRITICAL',
                   L_FAIL:      'FAIL    ',               #testrun fail/pass
                   L_PASS:      'PASS    ',    
                   L_SUCCESS:   'SUCCESS ',
                  }
    #default color scheme
    COLOR_SCHEME_DEFAULT = { 
                   #L_DEBUG:     Color.black,
                   #L_INFO:      Color.black,
                   L_WARNING:    Color.yellow,
                   L_ERROR:      Color.red,
                   L_CRITICAL:   Color.bold+Color.red,
                   L_FAIL:       Color.purple,
                   L_PASS:       Color.green,    
                   #L_SUCCESS:   Color.cyan,
                  }
    
    colorscheme= None
    # flags
    print_stats_on_exit = False   
    
    #initial counter va
    testcase_number=1                   #number the testcases, start number
    lnr=0                               #may be used from outside as a global counter
    
    stats = {}                          #holds all the counters for the loglevels
                                        #other loglevel stats will be autoadded here too
            
    #def __init__(self,**kwargs): 
    
    def __init__(self,
                 name=None,
                 loglevel=None,
                 logline_format=None,
                 logfile=None,
                 logfile_level=None,
                 print_stats_on_exit=False,
                 colorscheme=None,          #do not colorize                 
                 ):
        
        # check if 
        self._setDefaults(name=name, loglevel=loglevel, logline_format=logline_format,logfile=logfile,logfile_level=logfile_level,print_stats_on_exit=print_stats_on_exit,colorscheme=colorscheme)  #do defaults
        #self._setDefaults(kwargs)
        self._reinit()        

        return
    
    def _reinit(self):
        logging.Logger.__init__(self, self.qaNAME, self.qaLOGLEVEL)       
        logging.addLevelName(self.L_FAIL,"FAIL")
        logging.addLevelName(self.L_PASS,"PASS")    
        logging.addLevelName(self.L_SUCCESS,"SUCCESS")      

        #add default console handler
        console = logging.StreamHandler()
        console.setFormatter(self.qaFORMAT)
        
        self.addHandler(console)
        #add logfile handler 
        if self.qaLOGFILE!=None:
            self.enable_LogFile()
        return
    
    def _setDefaults(self,**kwargs):
        '''
            set some logging defaults
            
        '''
        #  ------ defaults for args -----------
        args = {'name':__name__,
                   'loglevel':self.defaultLOGLEVEL,
                   'logline_format':None,
                   'logfile':None,
                   'logfile_level':None,
                   'print_stats_on_exit':False,
                   'colorscheme':None}
        
        args.update(kwargs)
        name = args['name']
        loglevel=args['loglevel']
        logline_format=args['logline_format']
        logfile=args['logfile']
        logfile_level=args['logfile_level']
        print_stats_on_exit=args['print_stats_on_exit']
        colorscheme=args['colorscheme']
        
        # [format]
        if logline_format==None:
            #no value present, generate default
            self.qaFORMAT = logging.Formatter(self.defaultFORMAT)
        elif isinstance(logline_format,str):
            # lets generate it from string
            self.qaFORMAT = logging.Formatter(logline_format)
        elif isinstance(logline_format,logging.Formatter):
            # use the supplied formatter
            self.qaFORMAT=logline_format
        else:
            #throw exception
            pass
        #
        # [loglevel]
        #
        if loglevel==None:
            self.qaLOGLEVEL=self.defaultLOGLEVEL
        elif isinstance(loglevel,str):
            #parse string to loglevel
            if loglevel.upper == "DEBUG":
                self.qaLOGLEVEL=logging.DEBUG
            elif loglevel.upper=="INFO":
                self.qaLOGLEVEL=logging.INFO
            elif loglevel.upper=="WARNING":
                self.qaLOGLEVEL=logging.WARNING
            elif loglevel.upper=="CRITICAL":
                self.qaLOGLEVEL=logging.CRITICAL
            elif loglevel.upper=="ERROR":
                self.qaLOGLEVEL=logging.ERROR
            else:
                #throw exception!
                pass
        elif isinstance(loglevel,int):
            #use the supplied int or logging.WARNING(*) CONSTANT as loglevel
            self.qaLOGLEVEL=loglevel
        else:
            #throw exception
            pass
        #
        # [Name]
        #
        if isinstance(name,str):
            self.qaNAME=name
        else:
            self.qaNAME=self.defaultNAME
        #
        # [logfile]
        #
        if logfile!=None and isinstance(logfile,str):
            self.qaLOGFILE=logfile
        if isinstance(logfile_level,int):
            self.qaLOGFILE_LEVEL=logfile_level
        #
        # colorscheme
        #
        self.colorscheme=colorscheme
        #
        # stats on exit
        #
        self.print_stats_on_exit=print_stats_on_exit
        return
    
    def enable_LogFile(self,filename=None,level=None,format_line=None):
        # set up logging    
        if filename==None:
            filename=self.qaLOGFILE
        assert(filename != None)
            
        if level==None: level=self.qaLOGLEVEL
        if format_line==None: format_line=self.qaFORMAT
        
        fh = logging.FileHandler(filename)

        fh.setLevel(level)
        fh.setFormatter(format_line)
        self.addHandler(fh)
        return
      
    def _log(self, level, msg, args, exc_info=None, extra=None):
        #if not self.stats.has_key('Level%d'%(level)):
        #    self.stats.
        if self.stats.has_key('Level%d'%(level)):
            self.stats['Level%d'%(level)] +=1
        else:
            self.stats['Level%d'%(level)] =1 
        #return super(self.__class__,self)._log(level, msg, args, exc_info, extra)
        #fix for python <=2.5
        return logging.Logger._log(self, level, self.__colorize(msg,level), args, exc_info, extra)
    
    
    def __colorize(self,msg,level):
        if not self.colorscheme or not self.colorscheme.has_key(level): return msg
        
        return "%s%s%s"%(self.colorscheme[level],msg,Color.endc)
    
    '''
    ------------------------------------------------------------------------
    MIGRATE QA_Testrun to logger!
    ------------------------------------------------------------------------
    '''
    def print_stats(self):
        msgCount=0
        stats=None
        for k,v in self.stats.iteritems(): msgCount +=v         #count all messages

        if msgCount >0 :
            #only print status if there are msgs
            #print(self.getStats())      #auto log stats on exit
            stats=self.getStats()
            #self._log(1,"hiss")
            #self.info(stats)                     #deos not work
            #self.info("".join(stats))            #does not work
            print stats
        return stats       
    
    def __del__(self):
        if self.print_stats_on_exit: self.print_stats()
        
       
    ### -- testrun outcome stuff --
    
    def FAIL(self,message):
        self.log(self.L_FAIL,"[%s] - %s"%("FAIL",message))
        pass
    
    
    def PASS(self,message):
        self.log(self.L_PASS,"[%s] - %s"%("PASS",message))
        pass
    
    def SUCCESS(self,message):
        self.log(self.L_SUCCESS,"%s"%(message))
        pass
        
    ### -- testcase responsecheck stuff --
    
    def checkResponseAND(self,response,conditionDictionary,testcase_title=""):
        if conditionDictionary==None: return True
        for item,condition in conditionDictionary.iteritems():
                #get all items with condition
                if item in response:
                    #checkResponseBody is in data.. check if this is allowed
                    if condition==True:
                        # it is in data and expected to be there! PASS
                        self.debug("ok.. found valid: %s"%item)
                        
                    else:
                    # it is in data BUT shouldnt be there! FAIL -> RETURN
                        self.warning("NOT!.. found INVALID: %s"%item)
                        self.FAIL("-> %s"%(testcase_title))
                        return False
                        
                else:
                    #checkResponseBody is NOT in data, check if this is allowed
                    if condition==False:
                        # it is not in data, and expected not to be tehre! PASS
                        self.debug("ok.. did not find: %s"%item)
                    else:
                        # it is not in data, BUT expected to be there! FAIL
                        self.warning("NOT!.. found INVALID: %s"%item)
                        self.FAIL("-> %s"%(testcase_title))
                        return False
        self.PASS("-> %s"%(testcase_title))
        return True
        
    #### -- stats ---    
    
    def getStats(self):    
        '''
            Only returns stats matching the current loglevel filtering!
        '''   
        strStats = ""
        
        # pretty print overall stats (testcase based)
  
        numFailed=0
        if self.stats.has_key('Level%d'%(self.L_FAIL)):
            numFailed=self.stats['Level%d'%(self.L_FAIL)]
            
        numPassed=0
    
        if self.stats.has_key('Level%d'%(self.L_PASS)):
            numPassed=self.stats['Level%d'%(self.L_PASS)]
  
        
        if numFailed==0 and numPassed>0:
            strStats+="\t*** All tests PASSED!\n"
        elif numFailed+numPassed==0:
            strStats+=""
        elif numFailed==0:
            strStats+="\t*** Some tests FAILED!\n"
            
        numTotal = float(numFailed+numPassed)
        if numTotal<=0:numTotal=1
        
        strStats="%s\nTOTAL:%s   -   PASSED:%s   FAILED:%s    (%2.2f%%)"%(strStats,numFailed+numPassed,numPassed,numFailed,(100*float(numPassed)/numTotal))
            
            
        # pretty print logging stats at the end
        strStats +="\n\n\n--------------------------[Stats]--------------------------"
        
        lineitem=0
        strline=""
        
        # add all items from definitions array where the names are known
        # k=loglevel, v=str(name)
        for k,v in self.LL_to_Name.iteritems():
            if lineitem%3==0:               #newline after 3 items
                strline+="\n"
 
            if self.stats.has_key('Level%d'%(k)):
                #stats available
                cnt=self.stats['Level%d'%(k)]
            else:
                #no stats
                cnt=0
            
            strline+="%-8s:   %5d    "%(v,cnt)
            lineitem +=1           
            
            
        # now also add all leftovers
        strline+="\n\n"
        #k=Level# v=cnt
        for k,v in self.stats.iteritems():
            if lineitem%3==0:               #newline after 3 items
                strline+="\n"
            if self.LL_to_Name.has_key(int(filter(lambda x: x.isdigit(), k))):
                #loglevel exists in LL to name mapping, dont need to add this one as it was previously added (just above)
                pass
            else:
                #new stats for specific loglevel, printadd it
                strline+="%-8s:   %5d    "%(k,v)
                lineitem +=1                
        
                                                                           
        strStats +=strline      
        strStats +="\n-----------------------------------------------------------\n\n"
        return strStats
    
        
    def getNumFailed(self):
        return self.stats['Level%d'%(self.L_FAIL)]