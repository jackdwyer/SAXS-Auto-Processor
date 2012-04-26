"""
Jack Dwyer
17/02/2011
simulator that writes lines out to a 'live log'

20/02/2011
- Moved pre generated dat filles to simulation location
- setup the log file generation
TODO 
caput epics value.

23/12/2012
Will create folder structure from the entered data

------
Checks directory listing of scatterbrain .dat files, once a new file has appeared.
appends a line to the 'live log' and pushes '1' to a yet to be decided PV in EPICS 
the actual engine is listing to .
"""
import time
import epics
import glob
import shutil
import os
from LogLine import LogLine

absoluteLocation = "/home/jack/beamlinetesting/"

#Create User Directory:
def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

def makeLog(location):
    #make the log file
    liveLogFile = open(location+"raw_dat/livelogfile.log", "w")
    liveLogFile.close()

def main(user):
    dir = absoluteLocation+str(user)+"/"
    ensure_dir(dir)
    makeLog(dir)
    epics.caput("13SIM1:cam1:NumImages.VAL", 0, wait=True)
    

def run(user):
      
    #setup log generation 
    logFileName = "../data/livelogfile.log" #actual real log file prevous generated in another experiment
    log = open(logFileName)
    line = log.readline()
    
    
    print "******** Simulation Commenced **********"
    
    
    #list files in directory
    datFiles = glob.glob('/home/dwyerj/legitData/NK_dat/*.dat')
    
    x = 0 #index for datFileList
    time.sleep(2)
    while True:
        lineData = LogLine(line)
        fileLoc = lineData.data["ImageLocation"]
        liveLogFile = open(absoluteLocation+user+"/livelogfile.log", "a")
        epics.caput("13SIM1:cam1:NumImages.VAL", 0, wait=True)
        print epics.caget("13SIM1:cam1:NumImages_RBV")
        #get just filename
        
        fileName = fileLoc.split('/')
        fileName = fileName[-1]
        fileName = fileName.split('.')
        fileName = fileName[0] + ".dat"
        actualFileLoc = '../data/dat/'+fileName

        location = absoluateLocation + "raw_dat/"+fileName
        shutil.copy(actualFileLoc, location)
        print "Dat File: " + fileName + " Generated"
        
        #write a line out to the 'live' log    
        liveLogFile.write(line)
        liveLogFile.close()
        print "Line: " + line +  "- written to live log"   
        
        line = log.readline()
            
        #throw some data out to epics to let the actual python script know that there has been some images/shit happened
        epics.caput("13SIM1:cam1:NumImages.VAL", 100, wait=True)              
                       
        time.sleep(2)    
        
        #step up index of dat files
        x = x + 1
    
if __name__ == "__main__":
    user = raw_input("Please Enter User: ")
    main(user)
    raw_input("Press Enter to Start Simulation...")
    run(user)
    

