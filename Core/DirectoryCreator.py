"""
Jack Dwyer
1 April 2012

Class that generates all folders as specified by nigel/team saxs
it takes the absolute location and creates from there

"""

import os

class DirectoryCreator:
    def __init__(self, absolutePath):
        self.absolutePath = absolutePath
        self.user = ""
        self.experiment = ""
        self.fullPath = ""
        
    def createFolderStructure(self, rootDirectory, user):
        self.user = user
        self.fullPath = self.absolutePath + str(user) + "/"
        
        #Base Folder
        try:
            os.makedirs(self.fullPath)
        except OSError:
            pass
        
        #images
        try:
            os.makedirs(self.fullPath + "images/")
        except OSError:
            pass
        
        #raw_dat
        try:
            os.makedirs(self.fullPath + "raw_dat/")
        except OSError:
            pass
        
        #avg
        try:
            os.makedirs(self.fullPath + "avg/")
        except OSError:
            pass
        
        #sub
        try:
            os.makedirs(self.fullPath + "sub/")
        except OSError:
            pass
        
        #raw_sub (inside sub)
        try:
            os.makedirs(self.fullPath + "sub/raw_sub/")
        except OSError:
            pass
        
        #analysis
        try:
            os.makedirs(self.fullPath + "analysis/")
        except OSError:
            pass
        
        #manual
        try:
            os.makedirs(self.fullPath + "manual/")
        except OSError:
            pass
        
        #inner manual directories
        #raw_dat
        try:
            os.makedirs(self.fullPath + "manual/man_raw_dat/")
        except OSError:
            pass
        
        #man_avg
        try:
            os.makedirs(self.fullPath + "manual/man_avg/")
        except OSError:
            pass
        
        #man_sub
        try:
            os.makedirs(self.fullPath + "manual/man_sub/")
        except OSError:
            pass
        
        #man_raw_sub (inside sub)
        try:
            os.makedirs(self.fullPath + "manual/man_sub/man_raw_sub/")
        except OSError:
            pass
        
        #man_analysis
        try:
            os.makedirs(self.fullPath + "manual/man_analysis/")
        except OSError:
            pass
        
        
            


if __name__ == "__main__":
    folderBuilder = DirectoryCreator()
    folderBuilder.createFolderStructure("jack1")
        