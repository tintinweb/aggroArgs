aggroArgs
=========

Bruteforce commandline buffer overflows, linux, aggressive arguments


Usage
=========

	Usage: aggroArgs_v1_0.zip  [OPTIONS] [Argument(s) ...]
	
	Mandatory arguments to long options are mandatory for short options too.
	
	  -l <value>, --param-length=<value>         max length of a param passed to executable.
	                                             *** DEFAULT='999'
	  -R,         --no-recursion                 no recursive file scanning.
	  -p <value>, --params=<value>               number of params to supply.
	                                             *** DEFAULT='1'
	  -h,         --help                         This help.
	  -b <value>, --blacklist=<value>            Filename blacklists.
	                                             *** DEFAULT='*.so,*.so.*'
	  -t <value>, --process-timeout=<value>      max alive time of a process in seconds.
	                                             *** DEFAULT='5'
	  -v <value>, --verbosity=<value>            Enable verbose output.
	                                             *** DEFAULT='20'
	  -f <value>, --file-extensions=<value>      filter file extensions.
	                                             *** DEFAULT='None'
