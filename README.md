aggroArgs v1.3
===============

Tags: brute-force command-line based buffer overflows, aggressive arguments


*ProTip*: srsly, do NOT run this script in a productive environment (yes, this includes your workstation!) or things might get tricky :)

License: GPLv2 (see LICENSE)

Features
=========

* cyclic pattern overflows with automatic offset calculation
* segfault monitoring
* addr2line resolution
* commandline option probing
* exception based buffer overflow detection (stack_guard)
* will only scan ELF-Files marked as executable

Notes
=========

python 2.4

	#> unzip aggroArgs.zip
	#> python __main__.py --help


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
	  -m <value>, --modes=<value>                probe options (e.g. long,short,default).
	                                             *** DEFAULT='short,long,default'
	  -f <value>, --file-extensions=<value>      filter file extensions.
	                                             *** DEFAULT='None'

                            
	                                             
Use-Cases
==========

probe long, short and bruteforce commandline params skipping all *.so, *.so.* files and reboot,shutdown,runlevel,init

	#> aggroArgs.zip --blacklist=*.so,*.so.*,reboot,shutdown,runlevel,init,script /usr/bin                          
	                                             
probe short options only:

	#> aggroArgs.zip --modes=short --blacklist=*.so,*.so.*,reboot,shutdown,runlevel,init,script,rm /usr/bin  
	
verbose output  (DEBUG 10 ... 50 CRITICAL):

	#> aggroArgs.zip --verbosity=10 --blacklist=*.so,*.so.*,reboot,shutdown,runlevel,init,script,rm /usr/bin 
	
	
	
	
Live Action
============

Backtrack 5r1 scanning /usr/bin detected 31 buffer overflows.

	#> aggroArgs.zip --blacklist=*.so,*.so.*,reboot,shutdown,runlevel,init,script /usr/bin  
	...
	[2013-05-07 12:32:46,158] PASS - [PASS] - #78 - /usr/bin/hcitool 
	[2013-05-07 12:32:46,294] PASS - [PASS] - #79 - /usr/bin/grolbp 
	[2013-05-07 12:32:46,389] PASS - [PASS] - #79 - /usr/bin/grolbp 
	[2013-05-07 12:32:46,478] FAIL - [FAIL] - #79 - new log entries detected! - /usr/bin/grolbp 
	[2013-05-07 12:32:46,479] WARNING -      [79749.298667] grolbp[22911]: segfault at 0 ip b74c9b3c sp bf93838c error 4 in libc-2.11.1.so[b746a000+159000] 
	[2013-05-07 12:32:46,534] WARNING -      Addr2Line: ['??:0\n', '??:0\n'] 
	[2013-05-07 12:32:46,536] WARNING -      EIP_analysis: {'ip': 'b74c9b3c', 'sp': 'bf93838c', 'at': '0'} 
	[2013-05-07 12:32:46,643] PASS - [PASS] - #80 - /usr/bin/xcmsdb 
	[2013-05-07 12:32:46,764] PASS - [PASS] - #80 - /usr/bin/xcmsdb 
	[2013-05-07 12:32:46,969] PASS - [PASS] - #81 - /usr/bin/xvidtune 
	[2013-05-07 12:32:47,113] PASS - [PASS] - #81 - /usr/bin/xvidtune 
	...
	[2013-05-07 12:32:54,800] PASS - [PASS] - #99 - /usr/bin/411toppm 
	[2013-05-07 12:32:54,992] PASS - [PASS] - #100 - /usr/bin/pdbedit 
	[2013-05-07 12:32:55,158] PASS - [PASS] - #100 - /usr/bin/pdbedit 
	[2013-05-07 12:32:55,247] WARNING - Buffer overflow caught by stack_guard - /usr/bin/pdbedit 
	[2013-05-07 12:32:55,247] FAIL - [FAIL] - #100 - new log entries detected! - /usr/bin/pdbedit 
	[2013-05-07 12:32:55,248] WARNING -      ERROR: string overflow by 1 (256 - 255) in safe_strcpy [Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab]
	Username not found!
	...
	[2013-05-07 12:32:55,248] WARNING -      Addr2Line: [] 
	[2013-05-07 12:32:55,248] WARNING -      EIP_analysis: {} 
	[2013-05-07 12:32:55,430] PASS - [PASS] - #101 - /usr/bin/pngtopnm 
	[2013-05-07 12:32:55,546] PASS - [PASS] - #102 - /usr/bin/gcov-4.4 
	[2013-05-07 12:32:55,652] PASS - [PASS] - #102 - /usr/bin/gcov-4.4 
	[2013-05-07 12:32:55,732] PASS - [PASS] - #102 - /usr/bin/gcov-4.4 
	[2013-05-07 12:32:55,959] PASS - [PASS] - #103 - /usr/bin/xclipboard 
	[2013-05-07 12:32:56,148] PASS - [PASS] - #104 - /usr/bin/ssh-add 
	...
	[2013-05-07 12:34:01,007] PASS - [PASS] - #200 - /usr/bin/mysqlshow 
	[2013-05-07 12:34:01,204] FAIL - [FAIL] - #201 - new log entries detected! - /usr/bin/psnup 
	[2013-05-07 12:34:01,205] WARNING -      [79823.944166] psnup[25763]: segfault at bf909000 ip b766180c sp bf906658 error 6 in libc-2.11.1.so[b75ea000+159000] 
	[2013-05-07 12:34:01,247] WARNING -      Addr2Line: ['??:0\n', '??:0\n'] 
	[2013-05-07 12:34:01,251] WARNING -      EIP_analysis: {'ip': 'b766180c', 'sp': 'bf906658', 'at': 'bf909000', 'eip_ascii_real': '\x00\x90\x90\xbf', 'eip_ascii': '\xbf\x90\x90\x00'} 
	[2013-05-07 12:34:01,360] PASS - [PASS] - #202 - /usr/bin/bc 
	[2013-05-07 12:34:01,445] PASS - [PASS] - #202 - /usr/bin/bc 
	[2013-05-07 12:34:01,520] PASS - [PASS] - #202 - /usr/bin/bc 
	[2013-05-07 12:34:01,725] PASS - [PASS] - #203 - /usr/bin/doxygen 
	[2013-05-07 12:34:01,866] PASS - [PASS] - #203 - /usr/bin/doxygen
	...
	[2013-05-07 12:36:34,440] PASS - [PASS] - #476 - /usr/bin/pcretest 
	[2013-05-07 12:36:34,637] FAIL - [FAIL] - #477 - new log entries detected! - /usr/bin/xxxx 
	[2013-05-07 12:36:34,638] WARNING -      [79977.214970] xxxx[31856]: segfault at 30724139 ip b768a944 sp bff2e1c4 error 4 in libc-2.11.1.so[b765c000+159000] 
	[2013-05-07 12:36:34,685] WARNING -      Addr2Line: ['??:0\n', '??:0\n'] 
	[2013-05-07 12:36:34,689] WARNING -      EIP_analysis: {'eip_offset': 509, 'ip': 'b768a944', 'sp': 'bff2e1c4', 'eip_ascii_real': '9Ar0', 'at': '30724139', 'eip_ascii': '0rA9'} 
	[2013-05-07 12:36:34,896] PASS - [PASS] - #478 - /usr/bin/pulseaudio 
	[2013-05-07 12:36:35,072] PASS - [PASS] - #478 - /usr/bin/pulseaudio 
	[2013-05-07 12:36:35,186] PASS - [PASS] - #478 - /usr/bin/pulseaudio 
	...


	===[Summary]===
	[*] Path: /usr/bin
	
	  [0]---------------------------------------------------------
	     [ ] Path:      /usr/bin/grolbp
	     [ ] LogLines: 
	                [79749.298667] grolbp[22911]: segfault at 0 ip b74c9b3c sp bf93838c error 4 in libc-2.11.1.so[b746a000+159000]
	     [ ] Addr2Line: [['??:0\n', '??:0\n']]
	     [ ] EIP_Analysis: [{'ip': 'b74c9b3c', 'sp': 'bf93838c', 'at': '0'}]
	     [ ] Args:    
	                /usr/bin/grolbp 'Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9Ak0Ak1Ak2Ak3Ak4Ak5Ak6Ak7Ak8Ak9Al0Al1Al2Al3Al4Al5Al6Al7Al8Al9Am0Am1Am2Am3Am4Am5Am6Am7Am8Am9An0An1An2An3An4An5An6An7An8An9Ao0Ao1Ao2Ao3Ao4Ao5Ao6Ao7Ao8Ao9Ap0Ap1Ap2Ap3Ap4Ap5Ap6Ap7Ap8Ap9Aq0Aq1Aq2Aq3Aq4Aq5Aq6Aq7Aq8Aq9Ar0Ar1Ar2Ar3Ar4Ar5Ar6Ar7Ar8Ar9As0As1As2As3As4As5As6As7As8As9At0At1At2At3At4At5At6At7At8At9Au0Au1Au2Au3Au4Au5Au6Au7Au8Au9Av0Av1Av2Av3Av4Av5Av6Av7Av8Av9Aw0Aw1Aw2Aw3Aw4Aw5Aw6Aw7Aw8Aw9Ax0Ax1Ax2Ax3Ax4Ax5Ax6Ax7Ax8Ax9Ay0Ay1Ay2Ay3Ay4Ay5Ay6Ay7Ay8Ay9Az0Az1Az2Az3Az4Az5Az6Az7Az8Az9Ba0Ba1Ba2Ba3Ba4Ba5Ba6Ba7Ba8Ba9Bb0Bb1Bb2Bb3Bb4Bb5Bb6Bb7Bb8Bb9Bc0Bc1Bc2Bc3Bc4Bc5Bc6Bc7Bc8Bc9Bd0Bd1Bd2Bd3Bd4Bd5Bd6Bd7Bd8Bd9Be0Be1Be2Be3Be4Be5Be6Be7Be8Be9Bf0Bf1Bf2Bf3Bf4Bf5Bf6Bf7Bf8Bf9Bg0Bg1Bg2Bg3Bg4Bg5Bg6Bg7Bg8Bg9Bh0Bh1Bh2'
	
	  [1]---------------------------------------------------------
	     [ ] Path:      /usr/bin/pdbedit
	     [ ] LogLines: 
	                ERROR: string overflow by 1 (256 - 255) in safe_strcpy [Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab]
	Username not found!
	
	     [ ] Addr2Line: [[]]
	     [ ] EIP_Analysis: [{}]
	     [ ] Args:    
	                /usr/bin/pdbedit 'Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9Ak0Ak1Ak2Ak3Ak4Ak5Ak6Ak7Ak8Ak9Al0Al1Al2Al3Al4Al5Al6Al7Al8Al9Am0Am1Am2Am3Am4Am5Am6Am7Am8Am9An0An1An2An3An4An5An6An7An8An9Ao0Ao1Ao2Ao3Ao4Ao5Ao6Ao7Ao8Ao9Ap0Ap1Ap2Ap3Ap4Ap5Ap6Ap7Ap8Ap9Aq0Aq1Aq2Aq3Aq4Aq5Aq6Aq7Aq8Aq9Ar0Ar1Ar2Ar3Ar4Ar5Ar6Ar7Ar8Ar9As0As1As2As3As4As5As6As7As8As9At0At1At2At3At4At5At6At7At8At9Au0Au1Au2Au3Au4Au5Au6Au7Au8Au9Av0Av1Av2Av3Av4Av5Av6Av7Av8Av9Aw0Aw1Aw2Aw3Aw4Aw5Aw6Aw7Aw8Aw9Ax0Ax1Ax2Ax3Ax4Ax5Ax6Ax7Ax8Ax9Ay0Ay1Ay2Ay3Ay4Ay5Ay6Ay7Ay8Ay9Az0Az1Az2Az3Az4Az5Az6Az7Az8Az9Ba0Ba1Ba2Ba3Ba4Ba5Ba6Ba7Ba8Ba9Bb0Bb1Bb2Bb3Bb4Bb5Bb6Bb7Bb8Bb9Bc0Bc1Bc2Bc3Bc4Bc5Bc6Bc7Bc8Bc9Bd0Bd1Bd2Bd3Bd4Bd5Bd6Bd7Bd8Bd9Be0Be1Be2Be3Be4Be5Be6Be7Be8Be9Bf0Bf1Bf2Bf3Bf4Bf5Bf6Bf7Bf8Bf9Bg0Bg1Bg2Bg3Bg4Bg5Bg6Bg7Bg8Bg9Bh0Bh1Bh2'
			
	...
			
	TOTAL:2379   -   PASSED:2348   FAILED:31    (98.70%)
	
	
	--------------------------[Stats]--------------------------
	CRITICAL:       0    INFO    :     321    PASS    :    2348    
	SUCCESS :       0    FAIL    :      31    ERROR   :       0    
	DEBUG   :       0    WARNING :     119    
	
	
	-----------------------------------------------------------
	
	
				