""""
Jack DWyer
May 4 2012
SAXS - WAXS simulator/test harness for Auto Processor Engine
"""
import os
import sys
import time
import epics
import glob
import shutil

sys.path.append("../")


from Core.Logger import logger
import yaml
from threading import Thread
from Core import LogLine


class Sim:

    def __init__(self, configFile):
        #TODO Get the RBV then set X to that, so that we dont get a miss image taken

        self.name = "Simulator"
        #Load simulation configuration file
        try:
            stream = file(configFile, 'r') 
        except IOError:
            logger(self.name, "Unable to find configuration, exiting.")
            exit()
            
        self.config = yaml.load(stream)
        self.datFileLocation = self.config["datFileLocation"]
        self.RootDirectory = self.config["RootDirectory"]
        self.logFileLocation = self.config["LogFileLocation"]
        self.imageChangePV = self.config["imageChangePV"]
        self.userChangePV = self.config["userChangePV"]
        self.user = ""
        self.relative = self.user + "/images/"
        self.fullPath = ""
        self.liveLog = ""
        
        self.setUser()
        
        self.setImageLocationEpics()
        
        logger(self.name, "Sleeping 1second before generation of log")
        time.sleep(0.3)
        self.generateLog()
        self.run()
        
    
    def run(self):
        logger(self.name, "Started")
        self.logFile = open(self.logFileLocation)
        
        line = self.logFile.readline()
        datFiles = glob.glob(self.datFileLocation)
        
        x = epics.caget("13SIM1:cam1:NumImages.VAL")
        time.sleep(1)
        while True:
            lineData = LogLine.LogLine(line)
            fileLoc = lineData.data["ImageLocation"]
            #get just filename
        
            fileName = fileLoc.split('/')
            fileName = fileName[-1]
            fileName = fileName.split('.')
            fileName = fileName[0] + ".dat"
            actualFileLoc = self.datFileLocation+fileName

            location = self.RootDirectory + self.relative + "/raw_dat/" + fileName
            
            try:
                shutil.copy(actualFileLoc, location)
                logger(self.name, "Dat File, " + fileName + " Generated")

            except IOError:
                logger(self.name, "Dat File, " + fileName + " NOT FOUND")
                pass


        
            #write a line out to the 'live' log  
            time.sleep(0.1)
              
            liveLog = open(self.RootDirectory + self.relative + "/images/livelogfile.log", "a")
            print self.RootDirectory + self.relative
            liveLog.write(line)
            liveLog.close()
            epics.caput("13SIM1:cam1:NumImages.VAL", x + 1, wait=True)              

            print "Line: " + line +  "- written to live log"  
            
            #throw some data out to epics to let the actual python script know that there has been some images/shit happened
            line = self.logFile.readline()
            x = x + 1
            time.sleep(1)  
        
    def setRelative(self):
        self.relative =  self.user
    
    def setFullPath(self):
        self.fullPath = self.RootDirectory + self.user + "/images/"


    def pause(self):
        logger(self.name, "Function for pausing simulator")
            
    def start(self):
        logger(self.name, "starting simulator")
        
    def setUser(self):
        #For setting current EPN user
        self.user = raw_input('Enter User: ')
        self.setRelative()
        self.setFullPath()
        
    def setImageLocationEpics(self):
        epics.caput("13SIM1:TIFF1:FilePath", self.fullPath + bytearray("\0x00"*256))

    def generateLog(self):
        self.liveLog = open(self.RootDirectory + self.relative + "/images/livelogfile.log", "w")
        self.liveLog.close()
        
    

if __name__ == "__main__":
    sim = Sim("simconfig.yaml")
    #simThread = Thread(target=Sim, args=("simconfig.yaml",))
    #simThread.start()
    

    
    
    
