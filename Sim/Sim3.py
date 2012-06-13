"""
Jack Dwyer
06-07-2012
Better simulator, to send specific requests for testing
"""

import yaml
import time
import epics
import sys
import glob
import shutil


sys.path.append("../")
from Core import LogLine

class Sim3():
    def __init__(self, configuration):
        
        try:
            stream = file(configuration, 'r') 
        except IOError:
            logging.critical(self.name, "Unable to find configuration file (config.yaml, in current directory), exiting.")
            sys.exit
        
        config = yaml.load(stream)
        self.rootDirectory = config.get('RootDirectory')
        self.userChangePV = config.get('UserChangePV')   
        
        
        #Experiment Name might need to be implemented..
        
        #Some class Variables
        self.liveLog = None
        self.location = None
            
        
        self.run()
        
    def run(self):
        try:
            while True:
                print "1: Enter a User string"
                print "2: Send Repeat Request of same User"
                print "3: Send Repeat Request of different User"
                print "4: Start a Full Experiment"

    
                option = raw_input("Enter Option: ")
            
                
                if (option == "1"):
                    user = raw_input("Enter User: ")
                    self.sendUser(user)
                    
                if (option == "2"):
                    user = raw_input("Enter User: ")
                    timeout = raw_input("Enter timeout: ")
                    numOfTimes = raw_input("Number of runs: ")
                    i = 0
                    while (i < int(numOfTimes)):
                        self.sendUser(user)
                        time.sleep(float(timeout))
                        print i
                        i = i + 1                
        
                if (option == "3"):
                    timeout = raw_input("Enter timeout: ")
                    numOfTimes = raw_input("Number of runs: ")
                    i = 0
                    user = "JackA"
                    while (i < int(numOfTimes)):
                        self.sendUser(user)
                        time.sleep(float(timeout))
                        print i
                        i = i + 1                
                        user = user + "_a"
                        
                        
                if (option == "4"):
                    user = raw_input("Enter User: ")
                    self.runExperiment(user)
                    
                    
        except KeyboardInterrupt:
            pass
    
    def sendUser(self, user):
        epics.caput(self.userChangePV, "/location/to/something/"+str(user)+"/images" + bytearray("\0x00"*256))

    def createLog(self, user):
        self.liveLog = open(self.rootDirectory + "/" + user + "/images/livelogfile.log", "w")
        
    def setLocation(self, user):
        self.location = self.rootDirectory + "/" + user + "/"
        
        
    def runExperiment(self, user):
        self.sendUser(user)
        self.setLocation(user)
        time.sleep(0.1) #Give some time for the engine to check directories, and create if needed
        self.createLog(user)
        
        self.logFile = open("../data/livelogfile.log")
        line = self.logFile.readline()
        datFiles = glob.glob("../data/data/")
        while True:
            lineData = LogLine.LogLine(line)
            datFile = lineData.data["ImageLocation"]
            
            
            fileName = datFile.split('/')
            fileName = fileName[-1]
            fileName = fileName.split('.')
            fileName = fileName[0] + ".dat"
                        
            try:
                
                shutil.copy("../data/dat/"+fileName, self.location + "/raw_dat/")
            
            except IOError, e:
                print e
                pass
            
            time.sleep(0.1)
            print "Ran"
            self.liveLog.write(line)
            
            line = self.logFile.readline()
        
        


if __name__ == "__main__":
    sim = Sim3("simsettings.conf")


