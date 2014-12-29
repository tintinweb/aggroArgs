aggroArgs v1.3.x
===============

Tags: brute-force command-line based buffer overflows, aggressive arguments


*ProTip*: srsly, do NOT run this script in a productive environment (yes, this includes your workstation!) or things might get tricky :)

License: GPLv2 (see LICENSE)

Features
=========

* cyclic pattern overflows with automatic offset calculation
* segfault monitoring
* addr2line 
* smart command-line option probing (long/short options)
* exception based buffer overflow detection
* only scan ELF-Files marked as executable
* autogenerate PoCs

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
	  -o <value>, --output-poc=<value>           output directory for exploit PoC's .
	                                             *** DEFAULT='None'
	  -f <value>, --filter=<value>               filter filenames (e.g. qmail*).
	                                             *** DEFAULT='None'
	  -h,         --help                         This help.
	  -p <value>, --params=<value>               number of params to supply.
	                                             *** DEFAULT='1'
	  -t <value>, --process-timeout=<value>      max alive time of a process in seconds.
	                                             *** DEFAULT='5'
	  -v <value>, --verbosity=<value>            Enable verbose output.
	                                             *** DEFAULT='20'
	  -m <value>, --modes=<value>                probe options (e.g. long,short,default).
	                                             *** DEFAULT='short,long,default'
	  -b <value>, --blacklist=<value>            Filename blacklists.
	                                             *** DEFAULT='*.so,*.so.*,dmesg,script,suspend,init,runlevel,reboot,shutdown,switchoff,*grep'
	        
	                                             
Use-Cases
==========

probe long, short and bruteforce commandline params skipping all *.so, *.so.* files and reboot,shutdown,runlevel,init

	#> python aggroArgs.zip --blacklist=*.so,*.so.*,reboot,shutdown,runlevel,init,script /usr/bin                          
	                                             
probe short options only:

	#> python aggroArgs.zip --modes=short --blacklist=*.so,*.so.*,reboot,shutdown,runlevel,init,script,rm /usr/bin  
	
verbose output  (DEBUG 10 ... 50 CRITICAL):

	#> python aggroArgs.zip --verbosity=10 --blacklist=*.so,*.so.*,reboot,shutdown,runlevel,init,script,rm /usr/bin 
	
generate standalone PoC and save it to ./pocs
	
	#> python aggroArgs.zip --blacklist=*.so,*.so.*,reboot,shutdown,runlevel,init,script --output-poc=./pocs /usr/bin 
	
	
	
Live Action
============

Backtrack 5r1 scanning /usr/bin detected 44 buffer overflows.

	#> python aggroArgs.zip --blacklist=*.so,*.so.*,reboot,shutdown,runlevel,init,script /usr/bin   > scan_usr_bin.txt
	[2013-05-07 12:52:44,716] INFO - Skipping blacklisted files: ['*.so', '*.so.*', 'reboot', 'shutdown', 'runlevel', 'init', 'script'] 
	[2013-05-07 12:52:44,717] INFO - option probing modes enabled: ['short', 'long', 'default'] 
	[2013-05-07 12:52:44,770] INFO - [*] #0 - processing: /usr/bin/mysqladmin 
	[2013-05-07 12:52:44,911] PASS - [PASS] -   [*] /usr/bin/mysqladmin (short)  
	[2013-05-07 12:52:45,079] PASS - [PASS] -   [*] /usr/bin/mysqladmin (long)  
	[2013-05-07 12:52:45,176] PASS - [PASS] -   [*] /usr/bin/mysqladmin (default)  
	[2013-05-07 12:52:45,192] INFO - [*] #1 - processing: /usr/bin/lockfile-touch 
	[2013-05-07 12:52:50,352] INFO - Timeout - /usr/bin/lockfile-touch 
	[2013-05-07 12:52:50,386] PASS - [PASS] -   [*] /usr/bin/lockfile-touch (default)  
	[2013-05-07 12:52:50,403] INFO - [*] #2 - processing: /usr/bin/ppmtopgm 
	[2013-05-07 12:52:50,602] PASS - [PASS] -   [*] /usr/bin/ppmtopgm (default)  
	[2013-05-07 12:52:50,651] INFO - [*] #3 - processing: /usr/bin/gnome-doc-prepare 
	[2013-05-07 12:52:50,805] PASS - [PASS] -   [*] /usr/bin/gnome-doc-prepare (short)  
	[2013-05-07 12:52:50,936] PASS - [PASS] -   [*] /usr/bin/gnome-doc-prepare (long)  
	[2013-05-07 12:52:51,067] PASS - [PASS] -   [*] /usr/bin/gnome-doc-prepare (default) 
	...
	[2013-05-07 12:57:07,610] INFO - [*] #142 - processing: /usr/bin/hcitool 
	[2013-05-07 12:57:07,722] PASS - [PASS] -   [*] /usr/bin/hcitool (short)  
	[2013-05-07 12:57:07,808] PASS - [PASS] -   [*] /usr/bin/hcitool (long)  
	[2013-05-07 12:57:07,920] PASS - [PASS] -   [*] /usr/bin/hcitool (default)  
	[2013-05-07 12:57:07,961] INFO - [*] #143 - processing: /usr/bin/grolbp 
	[2013-05-07 12:57:08,095] PASS - [PASS] -   [*] /usr/bin/grolbp (short)  
	[2013-05-07 12:57:08,203] PASS - [PASS] -   [*] /usr/bin/grolbp (long)  
	[2013-05-07 12:57:08,291] FAIL - [FAIL] -   [!] LogCheck failed! - /usr/bin/grolbp (default) 
	[2013-05-07 12:57:08,292] WARNING -      [81209.554321] grolbp[21192]: segfault at 0 ip b758eb3c sp bfbf7cac error 4 in libc-2.11.1.so[b752f000+159000] 
	[2013-05-07 12:57:08,333] WARNING -   [ ]     Addr2Line: ['??:0\n', '??:0\n'] 
	[2013-05-07 12:57:08,335] WARNING -   [ ]     EIP_analysis: {'ip': 'b758eb3c', 'sp': 'bfbf7cac', 'at': '0'} 
	...
	[2013-05-07 13:06:18,791] INFO - [*] #532 - processing: /usr/bin/censored
	[2013-05-07 13:06:19,004] FAIL - [FAIL] -   [!] LogCheck failed! - /usr/bin/censored (default) 
	[2013-05-07 13:06:19,005] WARNING -      [81759.678804] censored[30710]: segfault at 77413277 ip b7683944 sp bfa9b054 error 4 in libc-2.11.1.so[b7655000+159000] 
	[2013-05-07 13:06:19,047] WARNING -   [ ]     Addr2Line: ['??:0\n', '??:0\n'] 
	[2013-05-07 13:06:19,051] WARNING -   [ ]     EIP_analysis: {'eip_offset': 667, 'ip': 'b7683944', 'sp': 'bfa9b054', 'eip_ascii_real': 'w2Aw', 'at': '77413277', 'eip_ascii': 'wA2w'} 
	[2013-05-07 13:06:19,097] INFO - [*] #533 - processing: /usr/bin/Etbg_update_list 
	[2013-05-07 13:06:19,314] PASS - [PASS] -   [*] /usr/bin/Etbg_update_list (default)  
	...

	
	
	===[Summary]===
	[*] Path: /usr/bin
	
	  [0]---------------------------------------------------------
	     [ ] Path:      /usr/bin/xxxxxxxxx
	     [ ] LogLines: 
	                *** glibc detected *** /usr/bin/mpost: malloc(): memory corruption: 0x08370c80 ***
	======= Backtrace: =========
	/lib/tls/i686/cmov/libc.so.6(+0x6e341)[0xb75f5341]
	/lib/tls/i686/cmov/libc.so.6(+0x71145)[0xb75f8145]
	/lib/tls/i686/cmov/libc.so.6(__libc_malloc+0x5c)[0xb75f9d4c]
	/lib/tls/i686/cmov/libc.so.6(__strdup+0x30)[0xb75fd260]
	/usr/bin/xxxxxxxxx[0x804995e]
	/usr/bin/xxxxxxxxx[0x804b2ee]
	/lib/tls/i686/cmov/libc.so.6(__libc_start_main+0xe6)[0xb759dbd6]
	/usr/bin/xxxxxxxxx[0x8049821]
	======= Memory map: ========
	08048000-080b4000 r-xp 00000000 08:01 176440     /usr/bin/xxxxxxxxx
	080b4000-080b5000 r--p 0006b000 08:01 176440     /usr/bin/xxxxxxxxx
	080b5000-080b6000 rw-p 0006c000 08:01 176440     /usr/bin/xxxxxxxxx
	080b6000-080b7000 rw-p 00000000 00:00 0 
	0834c000-083b1000 rw-p 00000000 00:00 0          [heap]
	b7400000-b7421000 rw-p 00000000 00:00 0 
	b7421000-b7500000 ---p 00000000 00:00 0 
	b7567000-b7584000 r-xp 00000000 08:01 266617     /lib/libgcc_s.so.1
	b7584000-b7585000 r--p 0001c000 08:01 266617     /lib/libgcc_s.so.1
	b7585000-b7586000 rw-p 0001d000 08:01 266617     /lib/libgcc_s.so.1
	b7586000-b7587000 rw-p 00000000 00:00 0 
	b7587000-b76e0000 r-xp 00000000 08:01 281274     /lib/tls/i686/cmov/libc-2.11.1.so
	b76e0000-b76e2000 r--p 00159000 08:01 281274     /lib/tls/i686/cmov/libc-2.11.1.so
	b76e2000-b76e3000 rw-p 0015b000 08:01 281274     /lib/tls/i686/cmov/libc-2.11.1.so
	b76e3000-b76e7000 rw-p 00000000 00:00 0 
	b76e7000-b770b000 r-xp 00000000 08:01 281268     /lib/tls/i686/cmov/libm-2.11.1.so
	b770b000-b770c000 r--p 00023000 08:01 281268     /lib/tls/i686/cmov/libm-2.11.1.so
	b770c000-b770d000 rw-p 00024000 08:01 281268     /lib/tls/i686/cmov/libm-2.11.1.so
	b770d000-b7721000 r-xp 00000000 08:01 289240     /usr/lib/libkpathsea.so.5.0.0
	b7721000-b7722000 r--p 00013000 08:01 289240     /usr/lib/libkpathsea.so.5.0.0
	b7722000-b7723000 rw-p 00014000 08:01 289240     /usr/lib/libkpathsea.so.5.0.0
	b7723000-b7725000 rw-p 00000000 00:00 0 
	b7737000-b7739000 rw-p 00000000 00:00 0 
	b7739000-b773a000 r-xp 00000000 00:00 0          [vdso]
	b773a000-b7755000 r-xp 00000000 08:01 281235     /lib/ld-2.11.1.so
	b7755000-b7756000 r--p 0001a000 08:01 281235     /lib/ld-2.11.1.so
	b7756000-b7757000 rw-p 0001b000 08:01 281235     /lib/ld-2.11.1.so
	bfd5b000-bfd7f000 rw-p 00000000 00:00 0          [stack]
	
	    [ ] Addr2Line: [[]]
	     [ ] EIP_Analysis: [{}]
	     [ ] Args:    
	                /usr/bin/xxxxxxxxx '-ini'   ...truncated...
	
	  [12]---------------------------------------------------------
	     [ ] Path:      /usr/bin/xxxx
	     [ ] LogLines: 
	                [81759.678804] xxxx[30710]: segfault at 77413277 ip b7683944 sp bfa9b054 error 4 in libc-2.11.1.so[b7655000+159000]
	     [ ] Addr2Line: [['??:0\n', '??:0\n']]
	     [ ] EIP_Analysis: [{'eip_offset': 667, 'ip': 'b7683944', 'sp': 'bfa9b054', 'eip_ascii_real': 'w2Aw', 'at': '77413277', 'eip_ascii': 'wA2w'}]
	     [ ] Args:    
	                /usr/bin/xxxx 'Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9Ak0Ak1Ak2Ak3Ak4Ak5Ak6Ak7Ak8Ak9Al0Al1Al2Al3Al4Al5Al6Al7Al8Al9Am0Am1Am2Am3Am4Am5Am6Am7Am8Am9An0An1An2An3An4An5An6An7An8An9Ao0Ao1Ao2Ao3Ao4Ao5Ao6Ao7Ao8Ao9Ap0Ap1Ap2Ap3Ap4Ap5Ap6Ap7Ap8Ap9Aq0Aq1Aq2Aq3Aq4Aq5Aq6Aq7Aq8Aq9Ar0Ar1Ar2Ar3Ar4Ar5Ar6Ar7Ar8Ar9As0As1As2As3As4As5As6As7As8As9At0At1At2At3At4At5At6At7At8At9Au0Au1Au2Au3Au4Au5Au6Au7Au8Au9Av0Av1Av2Av3Av4Av5Av6Av7Av8Av9Aw0Aw1Aw2Aw3Aw4Aw5Aw6Aw7Aw8Aw9Ax0Ax1Ax2Ax3Ax4Ax5Ax6Ax7Ax8Ax9Ay0Ay1Ay2Ay3Ay4Ay5Ay6Ay7Ay8Ay9Az0Az1Az2Az3Az4Az5Az6Az7Az8Az9Ba0Ba1Ba2Ba3Ba4Ba5Ba6Ba7Ba8Ba9Bb0Bb1Bb2Bb3Bb4Bb5Bb6Bb7Bb8Bb9Bc0Bc1Bc2Bc3Bc4Bc5Bc6Bc7Bc8Bc9Bd0Bd1Bd2Bd3Bd4Bd5Bd6Bd7Bd8Bd9Be0Be1Be2Be3Be4Be5Be6Be7Be8Be9Bf0Bf1Bf2Bf3Bf4Bf5Bf6Bf7Bf8Bf9Bg0Bg1Bg2Bg3Bg4Bg5Bg6Bg7Bg8Bg9Bh0Bh1Bh2'
		
		
	TOTAL:3692   -   PASSED:3648   FAILED:44    (98.81%)
	
	
	--------------------------[Stats]--------------------------
	CRITICAL:       0    INFO    :    2569    PASS    :    3648    
	SUCCESS :       0    FAIL    :      44    ERROR   :       0    
	DEBUG   :       0    WARNING :     167    
	
	
	-----------------------------------------------------------



	
	....
	

Example PoC
============

	#! /usr/bin/env python
	# vim:ts=4:sw=4:expandtab
	'''Created on Tue May  7 15:28:47 2013
	
	@author:  aggroArgs /
	@contact: https://github.com/tintinweb/aggroArgs
	---------------------------------------------
	Outline (max 350 chars): 
	
	  [x] Target:      /usr/bin/grub-fstest
	     [ ] LogLines: 
	                [90298.398399] grub-fstest[4771]: segfault at 0 ip 08049782 sp bfe900f0 error 4 in grub-fstest[8048000+26000]
	     [ ] Addr2Line: [['??:0', '??:0']]
	     [ ] EIP_Analysis: [{'ip': '08049782', 'sp': 'bfe900f0', 'at': '0'}]
	     [ ] Args:    
	                /usr/bin/grub-fst
	---------------------------------------------
	'''
	import subprocess
	
	CMD = '/usr/bin/grub-fstest'
	ARGS = ['-r', 'Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9Ak0Ak1Ak2Ak3Ak4Ak5Ak6Ak7Ak8Ak9Al0Al1Al2Al3Al4Al5Al6Al7Al8Al9Am0Am1Am2Am3Am4Am5Am6Am7Am8Am9An0An1An2An3An4An5An6An7An8An9Ao0Ao1Ao2Ao3Ao4Ao5Ao6Ao7Ao8Ao9Ap0Ap1Ap2Ap3Ap4Ap5Ap6Ap7Ap8Ap9Aq0Aq1Aq2Aq3Aq4Aq5Aq6Aq7Aq8Aq9Ar0Ar1Ar2Ar3Ar4Ar5Ar6Ar7Ar8Ar9As0As1As2As3As4As5As6As7As8As9At0At1At2At3At4At5At6At7At8At9Au0Au1Au2Au3Au4Au5Au6Au7Au8Au9Av0Av1Av2Av3Av4Av5Av6Av7Av8Av9Aw0Aw1Aw2Aw3Aw4Aw5Aw6Aw7Aw8Aw9Ax0Ax1Ax2Ax3Ax4Ax5Ax6Ax7Ax8Ax9Ay0Ay1Ay2Ay3Ay4Ay5Ay6Ay7Ay8Ay9Az0Az1Az2Az3Az4Az5Az6Az7Az8Az9Ba0Ba1Ba2Ba3Ba4Ba5Ba6Ba7Ba8Ba9Bb0Bb1Bb2Bb3Bb4Bb5Bb6Bb7Bb8Bb9Bc0Bc1Bc2Bc3Bc4Bc5Bc6Bc7Bc8Bc9Bd0Bd1Bd2Bd3Bd4Bd5Bd6Bd7Bd8Bd9Be0Be1Be2Be3Be4Be5Be6Be7Be8Be9Bf0Bf1Bf2Bf3Bf4Bf5Bf6Bf7Bf8Bf9Bg0Bg1Bg2Bg3Bg4Bg5Bg6Bg7Bg8Bg9Bh0Bh1Bh2', '-s', 'Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9Ak0Ak1Ak2Ak3Ak4Ak5Ak6Ak7Ak8Ak9Al0Al1Al2Al3Al4Al5Al6Al7Al8Al9Am0Am1Am2Am3Am4Am5Am6Am7Am8Am9An0An1An2An3An4An5An6An7An8An9Ao0Ao1Ao2Ao3Ao4Ao5Ao6Ao7Ao8Ao9Ap0Ap1Ap2Ap3Ap4Ap5Ap6Ap7Ap8Ap9Aq0Aq1Aq2Aq3Aq4Aq5Aq6Aq7Aq8Aq9Ar0Ar1Ar2Ar3Ar4Ar5Ar6Ar7Ar8Ar9As0As1As2As3As4As5As6As7As8As9At0At1At2At3At4At5At6At7At8At9Au0Au1Au2Au3Au4Au5Au6Au7Au8Au9Av0Av1Av2Av3Av4Av5Av6Av7Av8Av9Aw0Aw1Aw2Aw3Aw4Aw5Aw6Aw7Aw8Aw9Ax0Ax1Ax2Ax3Ax4Ax5Ax6Ax7Ax8Ax9Ay0Ay1Ay2Ay3Ay4Ay5Ay6Ay7Ay8Ay9Az0Az1Az2Az3Az4Az5Az6Az7Az8Az9Ba0Ba1Ba2Ba3Ba4Ba5Ba6Ba7Ba8Ba9Bb0Bb1Bb2Bb3Bb4Bb5Bb6Bb7Bb8Bb9Bc0Bc1Bc2Bc3Bc4Bc5Bc6Bc7Bc8Bc9Bd0Bd1Bd2Bd3Bd4Bd5Bd6Bd7Bd8Bd9Be0Be1Be2Be3Be4Be5Be6Be7Be8Be9Bf0Bf1Bf2Bf3Bf4Bf5Bf6Bf7Bf8Bf9Bg0Bg1Bg2Bg3Bg4Bg5Bg6Bg7Bg8Bg9Bh0Bh1Bh2', '-n', 'Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9Ak0Ak1Ak2Ak3Ak4Ak5Ak6Ak7Ak8Ak9Al0Al1Al2Al3Al4Al5Al6Al7Al8Al9Am0Am1Am2Am3Am4Am5Am6Am7Am8Am9An0An1An2An3An4An5An6An7An8An9Ao0Ao1Ao2Ao3Ao4Ao5Ao6Ao7Ao8Ao9Ap0Ap1Ap2Ap3Ap4Ap5Ap6Ap7Ap8Ap9Aq0Aq1Aq2Aq3Aq4Aq5Aq6Aq7Aq8Aq9Ar0Ar1Ar2Ar3Ar4Ar5Ar6Ar7Ar8Ar9As0As1As2As3As4As5As6As7As8As9At0At1At2At3At4At5At6At7At8At9Au0Au1Au2Au3Au4Au5Au6Au7Au8Au9Av0Av1Av2Av3Av4Av5Av6Av7Av8Av9Aw0Aw1Aw2Aw3Aw4Aw5Aw6Aw7Aw8Aw9Ax0Ax1Ax2Ax3Ax4Ax5Ax6Ax7Ax8Ax9Ay0Ay1Ay2Ay3Ay4Ay5Ay6Ay7Ay8Ay9Az0Az1Az2Az3Az4Az5Az6Az7Az8Az9Ba0Ba1Ba2Ba3Ba4Ba5Ba6Ba7Ba8Ba9Bb0Bb1Bb2Bb3Bb4Bb5Bb6Bb7Bb8Bb9Bc0Bc1Bc2Bc3Bc4Bc5Bc6Bc7Bc8Bc9Bd0Bd1Bd2Bd3Bd4Bd5Bd6Bd7Bd8Bd9Be0Be1Be2Be3Be4Be5Be6Be7Be8Be9Bf0Bf1Bf2Bf3Bf4Bf5Bf6Bf7Bf8Bf9Bg0Bg1Bg2Bg3Bg4Bg5Bg6Bg7Bg8Bg9Bh0Bh1Bh2', '-c', 'Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9Ak0Ak1Ak2Ak3Ak4Ak5Ak6Ak7Ak8Ak9Al0Al1Al2Al3Al4Al5Al6Al7Al8Al9Am0Am1Am2Am3Am4Am5Am6Am7Am8Am9An0An1An2An3An4An5An6An7An8An9Ao0Ao1Ao2Ao3Ao4Ao5Ao6Ao7Ao8Ao9Ap0Ap1Ap2Ap3Ap4Ap5Ap6Ap7Ap8Ap9Aq0Aq1Aq2Aq3Aq4Aq5Aq6Aq7Aq8Aq9Ar0Ar1Ar2Ar3Ar4Ar5Ar6Ar7Ar8Ar9As0As1As2As3As4As5As6As7As8As9At0At1At2At3At4At5At6At7At8At9Au0Au1Au2Au3Au4Au5Au6Au7Au8Au9Av0Av1Av2Av3Av4Av5Av6Av7Av8Av9Aw0Aw1Aw2Aw3Aw4Aw5Aw6Aw7Aw8Aw9Ax0Ax1Ax2Ax3Ax4Ax5Ax6Ax7Ax8Ax9Ay0Ay1Ay2Ay3Ay4Ay5Ay6Ay7Ay8Ay9Az0Az1Az2Az3Az4Az5Az6Az7Az8Az9Ba0Ba1Ba2Ba3Ba4Ba5Ba6Ba7Ba8Ba9Bb0Bb1Bb2Bb3Bb4Bb5Bb6Bb7Bb8Bb9Bc0Bc1Bc2Bc3Bc4Bc5Bc6Bc7Bc8Bc9Bd0Bd1Bd2Bd3Bd4Bd5Bd6Bd7Bd8Bd9Be0Be1Be2Be3Be4Be5Be6Be7Be8Be9Bf0Bf1Bf2Bf3Bf4Bf5Bf6Bf7Bf8Bf9Bg0Bg1Bg2Bg3Bg4Bg5Bg6Bg7Bg8Bg9Bh0Bh1Bh2', '-d', 'Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9Ak0Ak1Ak2Ak3Ak4Ak5Ak6Ak7Ak8Ak9Al0Al1Al2Al3Al4Al5Al6Al7Al8Al9Am0Am1Am2Am3Am4Am5Am6Am7Am8Am9An0An1An2An3An4An5An6An7An8An9Ao0Ao1Ao2Ao3Ao4Ao5Ao6Ao7Ao8Ao9Ap0Ap1Ap2Ap3Ap4Ap5Ap6Ap7Ap8Ap9Aq0Aq1Aq2Aq3Aq4Aq5Aq6Aq7Aq8Aq9Ar0Ar1Ar2Ar3Ar4Ar5Ar6Ar7Ar8Ar9As0As1As2As3As4As5As6As7As8As9At0At1At2At3At4At5At6At7At8At9Au0Au1Au2Au3Au4Au5Au6Au7Au8Au9Av0Av1Av2Av3Av4Av5Av6Av7Av8Av9Aw0Aw1Aw2Aw3Aw4Aw5Aw6Aw7Aw8Aw9Ax0Ax1Ax2Ax3Ax4Ax5Ax6Ax7Ax8Ax9Ay0Ay1Ay2Ay3Ay4Ay5Ay6Ay7Ay8Ay9Az0Az1Az2Az3Az4Az5Az6Az7Az8Az9Ba0Ba1Ba2Ba3Ba4Ba5Ba6Ba7Ba8Ba9Bb0Bb1Bb2Bb3Bb4Bb5Bb6Bb7Bb8Bb9Bc0Bc1Bc2Bc3Bc4Bc5Bc6Bc7Bc8Bc9Bd0Bd1Bd2Bd3Bd4Bd5Bd6Bd7Bd8Bd9Be0Be1Be2Be3Be4Be5Be6Be7Be8Be9Bf0Bf1Bf2Bf3Bf4Bf5Bf6Bf7Bf8Bf9Bg0Bg1Bg2Bg3Bg4Bg5Bg6Bg7Bg8Bg9Bh0Bh1Bh2', '-V', 'Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9Ak0Ak1Ak2Ak3Ak4Ak5Ak6Ak7Ak8Ak9Al0Al1Al2Al3Al4Al5Al6Al7Al8Al9Am0Am1Am2Am3Am4Am5Am6Am7Am8Am9An0An1An2An3An4An5An6An7An8An9Ao0Ao1Ao2Ao3Ao4Ao5Ao6Ao7Ao8Ao9Ap0Ap1Ap2Ap3Ap4Ap5Ap6Ap7Ap8Ap9Aq0Aq1Aq2Aq3Aq4Aq5Aq6Aq7Aq8Aq9Ar0Ar1Ar2Ar3Ar4Ar5Ar6Ar7Ar8Ar9As0As1As2As3As4As5As6As7As8As9At0At1At2At3At4At5At6At7At8At9Au0Au1Au2Au3Au4Au5Au6Au7Au8Au9Av0Av1Av2Av3Av4Av5Av6Av7Av8Av9Aw0Aw1Aw2Aw3Aw4Aw5Aw6Aw7Aw8Aw9Ax0Ax1Ax2Ax3Ax4Ax5Ax6Ax7Ax8Ax9Ay0Ay1Ay2Ay3Ay4Ay5Ay6Ay7Ay8Ay9Az0Az1Az2Az3Az4Az5Az6Az7Az8Az9Ba0Ba1Ba2Ba3Ba4Ba5Ba6Ba7Ba8Ba9Bb0Bb1Bb2Bb3Bb4Bb5Bb6Bb7Bb8Bb9Bc0Bc1Bc2Bc3Bc4Bc5Bc6Bc7Bc8Bc9Bd0Bd1Bd2Bd3Bd4Bd5Bd6Bd7Bd8Bd9Be0Be1Be2Be3Be4Be5Be6Be7Be8Be9Bf0Bf1Bf2Bf3Bf4Bf5Bf6Bf7Bf8Bf9Bg0Bg1Bg2Bg3Bg4Bg5Bg6Bg7Bg8Bg9Bh0Bh1Bh2', '-v', 'Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9Ak0Ak1Ak2Ak3Ak4Ak5Ak6Ak7Ak8Ak9Al0Al1Al2Al3Al4Al5Al6Al7Al8Al9Am0Am1Am2Am3Am4Am5Am6Am7Am8Am9An0An1An2An3An4An5An6An7An8An9Ao0Ao1Ao2Ao3Ao4Ao5Ao6Ao7Ao8Ao9Ap0Ap1Ap2Ap3Ap4Ap5Ap6Ap7Ap8Ap9Aq0Aq1Aq2Aq3Aq4Aq5Aq6Aq7Aq8Aq9Ar0Ar1Ar2Ar3Ar4Ar5Ar6Ar7Ar8Ar9As0As1As2As3As4As5As6As7As8As9At0At1At2At3At4At5At6At7At8At9Au0Au1Au2Au3Au4Au5Au6Au7Au8Au9Av0Av1Av2Av3Av4Av5Av6Av7Av8Av9Aw0Aw1Aw2Aw3Aw4Aw5Aw6Aw7Aw8Aw9Ax0Ax1Ax2Ax3Ax4Ax5Ax6Ax7Ax8Ax9Ay0Ay1Ay2Ay3Ay4Ay5Ay6Ay7Ay8Ay9Az0Az1Az2Az3Az4Az5Az6Az7Az8Az9Ba0Ba1Ba2Ba3Ba4Ba5Ba6Ba7Ba8Ba9Bb0Bb1Bb2Bb3Bb4Bb5Bb6Bb7Bb8Bb9Bc0Bc1Bc2Bc3Bc4Bc5Bc6Bc7Bc8Bc9Bd0Bd1Bd2Bd3Bd4Bd5Bd6Bd7Bd8Bd9Be0Be1Be2Be3Be4Be5Be6Be7Be8Be9Bf0Bf1Bf2Bf3Bf4Bf5Bf6Bf7Bf8Bf9Bg0Bg1Bg2Bg3Bg4Bg5Bg6Bg7Bg8Bg9Bh0Bh1Bh2']
	
	if __name__=='__main__':
	    print "Target: %s"%CMD
	    print "[ ] executing, please stand by ..."
	    ret = subprocess.Popen([CMD]+ARGS, shell=False,stdout=subprocess.PIPE,stderr=subprocess.STDOUT) 
	    print "[*] done!"
	