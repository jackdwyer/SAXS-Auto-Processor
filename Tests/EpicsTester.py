import epics
import time


def getUser(path):
    """Splits file path, and returns only user"""
    user = path.split("/")
    user = filter(None, user) #needed to remove the none characters from the array
    return user[-1] #currently the user_epn is the last object in the list

def userChange(char_value, **kw):
    user = getUser(char_value) #get new user
    return user

def monitorUser():
    epics.camonitor("13SIM1:TIFF1:FilePath_RBV", callback=userChange)


if __name__ == "__main__":
    epics.caput("13SIM1:TIFF1:FilePath", "/jack/natha" + bytearray("\0x00"*256))
    epics.caput("13SIM1:TIFF1:FilePath", "/jack/yahooo" + bytearray("\0x00"*256))
    

