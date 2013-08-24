'''
Created on 24.08.2013

@author: martin
'''

import os,fnmatch

class Scanner(object):
    def __init__(self, path, filter=None,blacklist=None, recursive=True):
        self.path = path
        self.filter = filter
        self.recursive= recursive
        self.blacklist = blacklist 
         
    def walk(self,path=None, filter=None, blacklist=None, recursive=None):
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