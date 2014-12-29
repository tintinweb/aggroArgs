'''
Created on Dec 27, 2014

@author: tintinweb

Smarter Usage Parser that tries to figure out semantics for usage lines to
increase coverage. Pretty Hacky... 

'''
import collections
import re

# custom token classes for reconstruction
class TToken(object):
    def __init__(self, e):
        self.e=e
        self.typ = self.__class__.__name__
    def __repr__(self):
        return "%s<%s>"%(self.__class__.__name__,repr(self.e))
    def __id__(self):
        return id(self.e)
    def __str__(self):
        return "".join(self.e)   # serialize lists
    
class TOptional(TToken):
    def __init__(self):
        self.typ = self.__class__.__name__
        self.e=[]
    def append(self, ee):
        self.e.append(ee)
        
class TOpt(object): 
    def __init__(self, e, requires_value=False, islong=False):
        self.e=e
        self.typ = self.__class__.__name__
        self.requires_value=False
        self.islong = False
    def __repr__(self):
        return "%s<requires_value=%s islong=%s %s>"%(self.__class__.__name__,self.requires_value, self.islong,repr(self.e))
    def __id__(self):
        return id(self.e)
    def __str__(self):
        return "".join(self.e)   # serialize lists

class TConst(TToken):pass
class TOr(TToken): pass
class TWord(TOptional): pass
class TVar(TToken):pass
class TBrk(TToken):pass

# parser tokenclass
Token = collections.namedtuple('Token', ['typ', 'value', 'line', 'column'])

class UsageParser(object):
    def __init__(self, intext, appname=None):
        self.intext = intext
        self.appname = appname
        self.observed_options = set([])           # track all individual options
        
    def _parse(self,):
        return self._tokenize(intext=self.intext)

    def _build_argchain(self):
        '''figure out what was just lexed..'''
        chain = []
        prev_token = None
        
        stack = []
        state = set([])
        break_chop = False
        
        for tok in self._tokenize(intext=self.intext):
            #print tok
            if tok.typ == 'APPNAME':
                # skip appname
                # start new
                if chain and not isinstance(chain[-1],TBrk):
                # insert Break on line changes to potentially abbr. some semantics
                    #chain.append(TBrk(''))
                    break_chop=True
                pass
            elif tok.typ == 'WORD':
                # skip WORD+ and only allow OPT+WORD
                if prev_token:
                    if  prev_token.typ in ('OPT_LONG','OPT_SHORT','OPT_ALT','OPTIONAL_START','OPTIONAL_END') and prev_token.line==tok.line and tok.column-(prev_token.column+len(prev_token.value))<=2:
                        if tok.value.strip().count(' ')<1:
                            stack.append(TVar(tok.value.strip()))
                    elif stack and (prev_token.typ ==tok.typ):
                        # got WORD+, clear stack
                        stack=[]
                        pass
                pass
            elif tok.typ in ('CONST'):
                stack.append(TVar(tok.value.strip()))
            elif tok.typ in ('OPT_LONG','OPT_SHORT','OPT_ALT'):
                o=TOpt(tok.value.strip())
                if tok.typ=='OPT_LONG':
                    o.islong=True
                self.observed_options.add(o)
                stack.append(o)
            elif tok.typ in ('OPTIONAL_START'):
                state.add('optional')
                stack = TOptional()
            elif tok.typ in ('OPTIONAL_END'):
                state.remove("optional")
            elif tok.typ in ('OR'):
                stack.append(TOr(tok.value.strip()))
            elif tok.typ in ("ASSIGN") and prev_token.typ in ('OPT_LONG','OPT_SHORT','OPT_ALT'):
                if "optional" in state:
                    src = stack
                else:
                    src = chain
                e = src.pop()
                e.requires_value=True
                src.append(e)
                
            if prev_token and tok.line != prev_token.line and chain and not chain[-1].typ in ('TBrk', 'TOr',):
                # insert Break on line changes to potentially abbr. some semantics
                #chain.append(TBrk(''))
                break_chop=True
                
            if stack and "optional" not in state: 
                if not isinstance(stack,list):
                    stack = [stack]         # fix stack

                if break_chop:
                    yield chain
                    break_chop=False
                    chain=[]

                chain +=stack
                stack=[]
                
            #yield tok
            prev_token = tok
        yield chain

        
    def _tokenize(self,intext):
        '''tokenize the input'''
        token_specification = [
            ('APPNAME',         self.appname), # Integer or decimal number
            ('NEWLINE',         r'\n'),          # Line endings
            ('OPT_LONG',        r'--[A-Za-z0-9\-]+'),   # Identifiers
            ('OPT_SHORT',       r'-[A-Za-z0-9]+'),   # Identifiers
            ('OPT_ALT',         r'\s{2,}[A-Za-z0-9]\s{2,}'),   # Identifiers
            ('OPTIONAL_START',  r'\['),    
            ('OPTIONAL_END',    r'\]'),
            ('OR',              r'\|'),
            ('CONST',           r'<\w+>'),                
            ('ASSIGN',          r'='),          # Assignment operator
            
            ('SKIP',            r'[ \t]+'),      # Skip over spaces and tabs
            ('SKIP_OTHER',      r'(<-|\.|\(|\)|,|`|\'|\~|\:|\*|\/|>|<|@|\?|;|\+|\-)'), # verbose skip
            ('WORD',            r'[\d\w]+[\.\-\w\d\:]*'),
            ('MISMATCH',        r'.'),           # Any other character
        ]
        tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
        line_num = 1
        line_start = 0
        for mo in re.finditer(tok_regex, intext):
            typ = mo.lastgroup
            value = mo.group(typ)
            if typ == 'NEWLINE':
                line_start = mo.end()
                line_num += 1
            elif typ in ('SKIP','SKIP_OTHER'):
                pass
            elif typ == 'MISMATCH':
                #continue
                pass
                #raise RuntimeError('%r unexpected on line %d' % (value, line_num))
            else:
                column = mo.start() - line_start
                yield Token(typ, value, line_num, column)

def _interpret_chains(chain):
    res = []
    for o in chain:
        if  o.typ=="TOptional":
            # skip TOptional for now.. just deref it
            res += _interpret_chains(o.e)
        elif o.typ=="TVar":
            # replace with cyclic pattern
            res.append('<CYCLIC>')
        elif o.typ=="TOpt":
            res.append(str(o))
        '''
        else:
            raise Exception("ERROR + %s"%o.typ)
        '''
    return res    
    
if __name__=='__main__':
    txt=''' Try 'ps --help <simple|list|output|threads|misc|all>'
  or 'ps --help <s|l|o|t|m|a>'
 for additional help text.
    '''

    txt='''
    For info, please visit https://www.isc.org/software/dhcp/
    Usage: dhclient [-4|-6] [-SNTP1dvrx] [-nw] [-p <port>] [-D LL|LLT]
                    [-s server-addr] [-cf config-file] [-lf lease-file]
                    [-pf pid-file] [--no-pid] [-e VAR=val]
                    [-sf script-file] [interface]
    '''
    txt='''Usage: tar -[cxtZzJjahmvO] [-X FILE] [-T FILE] [-f TARFILE] [-C DIR] [FILE]...
    
    Create, extract, or list files from a tar file
    
    Operation:
            c       Create
            x       Extract
            t       List
            f       Name of TARFILE ('-' for stdin/out)
            C       Change to DIR before operation
            v       Verbose
            Z       (De)compress using compress
            z       (De)compress using gzip
            J       (De)compress using xz
            j       (De)compress using bzip2
            a       (De)compress using lzma
            O       Extract to stdout
            h       Follow symlinks
            m       Don't restore mtime
            exclude File to exclude
            X       File with names to exclude
            T       File with names to include
    '''
    
    txt = '''Usage: ls [OPTION]... [FILE]...
    List information about the FILEs (the current directory by default).
    Sort entries alphabetically if none of -cftuvSUX nor --sort is specified.
    
    Mandatory arguments to long options are mandatory for short options too.
      -a, --all                  do not ignore entries starting with .
      -A, --almost-all           do not list implied . and ..
          --author               with -l, print the author of each file
      -b, --escape               print C-style escapes for nongraphic characters
          --block-size=SIZE      scale sizes by SIZE before printing them.  E.g.,
                                   `--block-size=M' prints sizes in units of
                                   1,048,576 bytes.  See SIZE format below.
      -B, --ignore-backups       do not list implied entries ending with ~
      -c                         with -lt: sort by, and show, ctime (time of last
                                   modification of file status information)
                                   with -l: show ctime and sort by name
                                   otherwise: sort by ctime, newest first
      -C                         list entries by columns
          --color[=WHEN]         colorize the output.  WHEN defaults to `always'
                                   or can be `never' or `auto'.  More info below
      -d, --directory            list directory entries instead of contents,
                                   and do not dereference symbolic links
      -D, --dired                generate output designed for Emacs' dired mode
      -f                         do not sort, enable -aU, disable -ls --color
      -F, --classify             append indicator (one of */=>@|) to entries
          --file-type            likewise, except do not append `*'
          --format=WORD          across -x, commas -m, horizontal -x, long -l,
                                   single-column -1, verbose -l, vertical -C
          --full-time            like -l --time-style=full-iso
      -g                         like -l, but do not list owner
          --group-directories-first
                                 group directories before files.
                                   augment with a --sort option, but any
                                   use of --sort=none (-U) disables grouping
      -G, --no-group             in a long listing, don't print group names
      -h, --human-readable       with -l, print sizes in human readable format
                                   (e.g., 1K 234M 2G)
          --si                   likewise, but use powers of 1000 not 1024
      -H, --dereference-command-line
                                 follow symbolic links listed on the command line
          --dereference-command-line-symlink-to-dir
                                 follow each command line symbolic link
                                 that points to a directory
          --hide=PATTERN         do not list implied entries matching shell PATTERN
                                   (overridden by -a or -A)
          --indicator-style=WORD  append indicator with style WORD to entry names:
                                   none (default), slash (-p),
                                   file-type (--file-type), classify (-F)
      -i, --inode                print the index number of each file
      -I, --ignore=PATTERN       do not list implied entries matching shell PATTERN
      -k                         like --block-size=1K
      -l                         use a long listing format
      -L, --dereference          when showing file information for a symbolic
                                   link, show information for the file the link
                                   references rather than for the link itself
      -m                         fill width with a comma separated list of entries
      -n, --numeric-uid-gid      like -l, but list numeric user and group IDs
      -N, --literal              print raw entry names (don't treat e.g. control
                                   characters specially)
      -o                         like -l, but do not list group information
      -p, --indicator-style=slash
                                 append / indicator to directories
      -q, --hide-control-chars   print ? instead of non graphic characters
          --show-control-chars   show non graphic characters as-is (default
                                 unless program is `ls' and output is a terminal)
      -Q, --quote-name           enclose entry names in double quotes
          --quoting-style=WORD   use quoting style WORD for entry names:
                                   literal, locale, shell, shell-always, c, escape
      -r, --reverse              reverse order while sorting
      -R, --recursive            list subdirectories recursively
      -s, --size                 print the allocated size of each file, in blocks
      -S                         sort by file size
          --sort=WORD            sort by WORD instead of name: none -U,
                                 extension -X, size -S, time -t, version -v
          --time=WORD            with -l, show time as WORD instead of modification
                                 time: atime -u, access -u, use -u, ctime -c,
                                 or status -c; use specified time as sort key
                                 if --sort=time
          --time-style=STYLE     with -l, show times using style STYLE:
                                 full-iso, long-iso, iso, locale, +FORMAT.
                                 FORMAT is interpreted like `date'; if FORMAT is
                                 FORMAT1<newline>FORMAT2, FORMAT1 applies to
                                 non-recent files and FORMAT2 to recent files;
                                 if STYLE is prefixed with `posix-', STYLE
                                 takes effect only outside the POSIX locale
      -t                         sort by modification time, newest first
      -T, --tabsize=COLS         assume tab stops at each COLS instead of 8
      -u                         with -lt: sort by, and show, access time
                                   with -l: show access time and sort by name
                                   otherwise: sort by access time
      -U                         do not sort; list entries in directory order
      -v                         natural sort of (version) numbers within text
      -w, --width=COLS           assume screen width instead of current value
      -x                         list entries by lines instead of by columns
      -X                         sort alphabetically by entry extension
      -Z, --context              print any SELinux security context of each file
      -1                         list one file per line
          --help     display this help and exit
          --version  output version information and exit
    
    SIZE may be (or may be an integer optionally followed by) one of following:
    KB 1000, K 1024, MB 1000*1000, M 1024*1024, and so on for G, T, P, E, Z, Y.
    
    Using color to distinguish file types is disabled both by default and
    with --color=never.  With --color=auto, ls emits color codes only when
    standard output is connected to a terminal.  The LS_COLORS environment
    variable can change the settings.  Use the dircolors command to set it.
    
    Exit status:
     0  if OK,
     1  if minor problems (e.g., cannot access subdirectory),
     2  if serious trouble (e.g., cannot access command-line argument).
    
    Report ls bugs to bug-coreutils@gnu.org
    GNU coreutils home page: <http://www.gnu.org/software/coreutils/>
    General help using GNU software: <http://www.gnu.org/gethelp/>
    For complete documentation, run: info coreutils 'ls invocation'
    '''
    
    txt ='''Usage:
      arp [-vn]  [<HW>] [-i <if>] [-a] [<hostname>]             <-Display ARP cache
      arp [-v]          [-i <if>] -d  <host> [pub]               <-Delete ARP entry
      arp [-vnD] [<HW>] [-i <if>] -f  [<filename>]            <-Add entry from file
      arp [-v]   [<HW>] [-i <if>] -s  <host> <hwaddr> [temp]            <-Add entry
      arp [-v]   [<HW>] [-i <if>] -Ds <host> <if> [netmask <nm>] pub          <-''-
    
            -a                       display (all) hosts in alternative (BSD) style
            -s, --set                set a new ARP entry
            -d, --delete             delete a specified entry
            -v, --verbose            be verbose
            -n, --numeric            don't resolve names
            -i, --device             specify network interface (e.g. eth0)
            -D, --use-device         read <hwaddr> from given device
            -A, -p, --protocol       specify protocol family
            -f, --file               read new entries from file or from /etc/ethers
    
      <HW>=Use '-H <hw>' to specify hardware address type. Default: ether
      List of possible hardware types (which support ARP):
        strip (Metricom Starmode IP) ash (Ash) ether (Ethernet)
        tr (16/4 Mbps Token Ring) tr (16/4 Mbps Token Ring (New)) ax25 (AMPR AX.25)
        netrom (AMPR NET/ROM) rose (AMPR ROSE) arcnet (ARCnet)
        dlci (Frame Relay DLCI) fddi (Fiber Distributed Data I
    '''
    
    up = UsageParser(appname=None, intext=txt)
    for chain in up._build_argchain():
        print(chain)
        print _interpret_chains(chain)
    # get all long options
    for o in (oo for oo in up.observed_options if oo.islong==True):
        print o
    
