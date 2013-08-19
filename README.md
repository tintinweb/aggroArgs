aggroArgs v1.2
===============

Bruteforce commandline buffer overflows, linux, aggressive arguments


ProTip: do not run on your local machine or things might get tricky :)


Features
=========

* cyclic pattern overflows
* segfault monitoring
* addr2line resolution
* commandline option probing
* exception based buffer overflow detection (stack_guard)


Usage
=========

	Usage: aggroArgs.zip  [OPTIONS] [Argument(s) ...]
	
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
	                                             
	                                             
	                                             
