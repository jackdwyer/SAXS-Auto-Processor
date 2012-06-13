"""
Jack Dwyer
07-06-2012

Collection of Functions used by the Engine
"""

import os


def getUser(path):
    """Splits file path, and returns only user"""
    user = path.split("/")
    user = filter(None, user) #needed to remove the none characters from the array
    
    ###########################################################################################################
    #set to -2
    return user[-2] #
    ###########################################################################################################
    

def testUserChange(user, perviousUser):
    if not (perviousUser):
        return True
    else:
        if (perviousUser == user):
            return False
        if (perviousUser != user):
            return True
        
def createFolderStructure(rootDirectory, user):
    fullPath = rootDirectory + "/"+ user
   
    try:
        os.makedirs(fullPath)
        os.makedirs(fullPath + "/images/")
        os.makedirs(fullPath + "/raw_dat/")
        os.makedirs(fullPath + "/avg/")
        os.makedirs(fullPath + "/sub/")
        os.makedirs(fullPath + "/sub/raw_sub/")
        os.makedirs(fullPath + "/manual/")
        os.makedirs(fullPath + "/manual/man_raw_dat/")
        os.makedirs(fullPath + "/manual/man_avg/")
        os.makedirs(fullPath + "/manual/man_sub/")
        os.makedirs(fullPath + "/manual/man_sub/man_raw_sub/")
        os.makedirs(fullPath + "/manual/man_analysis/")
    except OSError:
        pass

        

def generateDirectoryStructure(rootDirectory):
    dirCreator = DirectoryCreator.DirectoryCreator(rootDirectory)
    dirCreator.createFolderStructure(self.user)
