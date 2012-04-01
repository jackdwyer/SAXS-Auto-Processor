#!/usr/bin/env python2.7
"""
Jack Dwyer
18 March 2012

Engine for the SAXS/WAXS Auto Processor
"""

import epics
import time
import zmq
from CommonLib import *
from CommonLib import Logger
import MySQLdb as mysql


class Engine():
    def __init__(self):
        self.name = "Engine" #For logging

        #ZeroMQ setup stuff
        self.context = zmq.Context()
        self.bufferWorker = self.context.socket(zmq.PUSH)
        self.bufferWorker.bind("tcp://127.0.0.1:7881")  
        self.sampleWorker = self.context.socket(zmq.PUSH)
        self.sampleWorker.bind("tcp://127.0.0.1:7882")
        #7883 is used by the WorkerBufferAverage
        self.dbWorker = self.context.socket(zmq.PUSH)
        self.dbWorker.bind("tcp://127.0.0.1:7884")
        #7885 is used for WorkerRollingAverageSubtraction
        self.rollingAverageWorker = self.context.socket(zmq.PUSH)
        self.rollingAverageWorker.bind("tcp://127.0.0.1:7885")        
        
        #To make sure we dont miss any loglines
        self.index = 0
        #User setup
        self.user = ""
        self.experiment = "EXPERIMENT_1"
        self.logFile = ""
        
        #File Locations
        self.logLocation = "testDat/livelogfile.log"
        self.datFileLocation = "/home/dwyerj/sim/"
        

        #For holding the data
        self.lines = [] #List of lines already read
        self.logLines = [] #List of LogLine Objects, that have been broken down for easy access
        self.latestLine = ""
        self.datFiles = []

        #Make sure all sockets are created
        time.sleep(1.0)
        
    def clear(self):
        """Clears out the Engine and all workers, should only occur when a new user has changed over"""
        Logger.log(self.name, "Commencing Clear out")
        self.index = 0
        self.user = ""
        self.experiment = "EXPERIMENT_1"
        self.logFile = ""
        
        self.lines = []
        self.logLines = []
        self.lastLine = ""
        self.datFiles = []
        
        self.bufferWorker.send("clear")
        self.sampleWorker.send("clear")
        
        Logger.log(self.name, "ENGINE and ALL WORKERS CLEARED")

        

    def generateDB(self):
        self.dbWorker.send("user")
        self.dbWorker.send(str(self.user))
        self.dbWorker.send("Experiment")
        self.dbWorker.send(str(self.experiment)) 
        
    
    def getUser(self, path):
        """Splits file path, and returns only user"""
        user = path.split("/")
        user = filter(None, user) #needed to remove the none characters from the array
        return user[-1] #currently the user_epn is the last object in the list
    
    def userChange(self, char_value, **kw):
        """Get the user_epn when a change over has occured, 
        this will create a new DB for the user, create directory structure
        and clear out all workers"""
        Logger.log(self.name, "User change over initiated")
        self.clear()
        user = self.getUser(char_value)
        self.user = user
        Logger.log(self.name, "NEW USER: " + str(self.user))
        
        self.generateDB()        
    
        #fix        self.logFile = "testDat/livelogfile_nk_edit.log" 
        
        #Setup Variables/File Locations for user
        self.logFile = "testDat/livelogfile_nk_edit.log"
         
    
    def imageTaken(self, value, **kw ):
        """Check Logline, get all details on latest image """
        Logger.log(self.name, "Image Value Changed - Shot Taken")
        
        if value == 100:
            self.readLatestLine()
            Logger.log(self.name, "Read Latest line from LogFile")
            self.getDatFile()
            Logger.log(self.name, "Retrieved DatFile")
           
            
            #print self.datFiles[self.index-1].getDatFilePath()
            
            
            imageType = (self.logLines[self.index-1].getValue("SMPL_TYPE"))
            
            #print imageType
            
            #if (imageType == "BUFFER"):
            if (imageType == "BUFFER"):
                Logger.log(self.name, "BUFFER")
                self.bufferWorker.send("datFile")
                self.bufferWorker.send_pyobj(self.datFiles[self.index-1])
                Logger.log(self.name, "sent DatFile to WorkerBuffer")
            if (imageType == "STATIC_SAMPLE"):
                Logger.log(self.name, "STATIC IMAGE")
                self.bufferWorker.send("sample")
                self.sampleWorker.send_pyobj(self.datFiles[self.index-1])
                Logger.log(self.name, "Sent DatFile to WorkerStaticImage")
                self.rollingAverageWorker.send_pyobj(self.datFiles[self.index-1])
                Logger.log(self.name, "Sent DatFile to WorkerRollingImage")







    def run(self):                       
        epics.camonitor("13SIM1:cam1:NumImages_RBV", callback=self.imageTaken)
        epics.camonitor("13SIM1:TIFF1:FilePath_RBV", callback=self.userChange)
 
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        
        
        
    
    
###These should go into generic methods
    def readLatestLine(self):
        noLines = True
        while (noLines):          
            try:
                Logger.log(self.name, "Opening LogFile")                
                v = open(self.logFile, "r")
                try:
                    self.latestLine = v.readlines()[self.index]
                    if (self.latestLine in self.lines):
                        time.sleep(0.05)
                    else:
                        self.lines.append(self.latestLine)
                        self.logLines.append(LogLine.LogLine(self.latestLine))
                        self.index = self.index + 1
                        
                        #Send logline to be added to DB
                        self.dbWorker.send("logLine")
                        self.dbWorker.send_pyobj(self.logLines[self.index-1])
                        
                        noLines = False
                except IndexError:
                    pass
                                
                v.close()
            except IOError:
                Logger.log(self.name, "IOERROR - trying to read last line from logfile")
                time.sleep(0.5)
                pass
            
        
    def getDatFile(self):
        """TODO: make better... forgot the better and faster way I had the imagename
        """
        ##returns dat file location
        noDatFile = True
        #getting actual dat file name from the log line. It will only pick up that dat file
        dat = self.logLines[self.index-1].getValue("ImageLocation")
        #this needs to be fixed to os agnostic
        dat = dat.split("/")
        dat = dat[-1]
        dat = dat.split(".")
        dat = dat[0] + ".dat"
        dat = str(dat)
        while (noDatFile):
            try:
                datFile = ('testDat/'+ dat)  
                self.datFiles.append(DatFile.DatFile(datFile))               
                noDatFile = False
            except IOError:
                time.sleep(0.05)



if __name__ == "__main__":
    engine = Engine()
    engine.run()
