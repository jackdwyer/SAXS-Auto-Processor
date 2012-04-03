#!/usr/bin/env python2.7
"""
Jack Dwyer
18 March 2012

Engine for the SAXS/WAXS Auto Processor
"""

import epics
import time
import zmq
from CommonLib import DatFile
from CommonLib import LogLine
from CommonLib import Logger
from CommonLib import DirectoryCreator
import MySQLdb as mysql


class Engine():
    def __init__(self):
        self.name = "Engine" #For logging

        self.absolutePath = "/home/ics/jack/beam/"
        self.directoryCreator = DirectoryCreator.DirectoryCreator(self.absolutePath)


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
        self.datIndex = 0
        #User setup
        self.user = ""
        self.experiment = "EXPERIMENT_1"
        self.logFile = "/mnt/images/data/Cycle_2012_1/Melton_4615/livelogfile.log"

        #File Locations
        self.logLocation = "/mnt/images/data/Cycle_2012_1/Melton_4615/livelogfile.log"
        #self.logLocation = "testDat/livelogfile.log"
        self.datFileLocation = "/mnt/images/data/Cycle_2012_1/Melton_4615/dat/"


        #For holding the data
        self.lines = [] #List of lines already read
        self.logLines = [] #List of LogLine Objects, that have been broken down for easy access
        self.latestLine = ""
        self.datFiles = []


        
        #comparision checks again datfile name
        self.lastDatFile = ""
        self.currentDatFile = ""


        #Make sure all sockets are created
        time.sleep(1.0)
        
    def clear(self):
        """Clears out the Engine and all workers, should only occur when a new user has changed over"""
        Logger.log(self.name, "Commencing Clear out")
        self.index = 0
        self.user = ""
        self.experiment = "EXPERIMENT_1"
        #self.logFile = ""

        self.lines = []
        self.logLines = []
        self.lastLine = ""
        self.datFiles = []

        self.bufferWorker.send("clear")
        self.sampleWorker.send("clear") 
        self.rollingAverageWorker.send("clear")

        self.lastDatFile = ""
        self.currentDatFile = ""    

        Logger.log(self.name, "ENGINE and ALL WORKERS CLEARED")
        

    def generateDB(self):
        self.dbWorker.send("user")
        self.dbWorker.send(str(self.user))
        self.dbWorker.send("Experiment")
        self.dbWorker.send(str(self.experiment)) 
        Logger.log(self.name, "Database Created - " + self.user)
        
    def updateWorkers(self):
                self.bufferWorker.send("user")
                self.bufferWorker.send(self.user)
                Logger.log(self.name, "sent new user to WorkerBuffer")
                self.bufferWorker.send(self.experiment)
                Logger.log(self.name, "sent new experiment to WorkerBuffer")



                self.sampleWorker.send("user")
                self.sampleWorker.send(self.user)
                Logger.log(self.name, "Sent new user to WorkerStaticImage")
                self.sampleWorker.send(self.experiment)
                Logger.log(self.name, "Sent new experiment to WorkerStaticImage")
                
                self.rollingAverageWorker.send("user")
                self.rollingAverageWorker.send(self.user)
                Logger.log(self.name, "Sent new user to WorkerRollingImage")
                self.rollingAverageWorker.send(self.experiment)
                Logger.log(self.name, "Sent new experiment to WorkerRollingImage")

        
        

        
    
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
        self.clear() #Clear engine, and all workers
        
        user = self.getUser(char_value) #get new user
        self.user = user
        Logger.log(self.name, "NEW USER: " + str(self.user))
        
        self.generateDB() 
        self.updateWorkers()
        
        self.directoryCreator.createFolderStructure(self.user, self.experiment);
        Logger.log(self.name, "Folder Structure Created")

    
        #fix        self.logFile = "testDat/livelogfile_nk_edit.log" 
        
        #Setup Variables/File Locations for user
        #self.logFile = "testDat/livelogfile_nk_edit.log"
        
    def getOnlyName(self, name):
        #TODO REFACTOR        
        b = name.split('_')
        del b[-1]
        return b

    def checkName(self):
        #TODO REFACTOR
        if (self.datIndex == 1) or (self.datIndex == 0):
            return False;
        else:
            previousName = self.datFiles[self.datIndex - 2].getFileName()
            currentName = self.datFiles[self.datIndex - 1].getFileName()
        prev = self.getOnlyName(previousName)
        cur = self.getOnlyName(currentName)

        if (cur == prev):  
            return True
        else:   
            return False
            




    #def imageTaken(self, value, **kw):
    def imageTaken(self):
        """Check Logline, get all details on latest image """
        Logger.log(self.name, "Image Value Changed - Shot Taken")
        
        #self.index = value #This is to foce the engine to begin where ever the experiment is
        self.readLatestLine()
        Logger.log(self.name, "Read Latest line from LogFile")
        self.getDatFile()
        Logger.log(self.name, "Retrieved DatFile")
       
        changeInName = self.checkName()
        #Here to test against sample change, then slap out for if its a buffer
        
                



        try:
            imageType = (self.logLines[self.index-1].data['SampleType'])
        except KeyError:
            Logger.log(self.name, "KeyError on SampleType, probably nothing")
            imageType = "12"



        if ((imageType == '0') and (changeInName)):
            Logger.log(self.name, "Root Name Change - Idicating Sample Change")
            Logger.log(self.name, "New Buffer Generated - Clearing Workers")
            self.bufferWorker.send("recalculate_buffer")
            self.sampleWorker.send("new_buffer")
            self.rollingAverageWorker.send("new_buffer")
        
        if ((changeInName) and (imageType != 0)):
            Logger.log(self.name, "Root Name Change - Idicating Sample Change")
            self.sampleWorker.send("new_sample")
            self.rollingAverageWorker.send("new_sample")



        #print self.datFiles[self.index-1].getDatFilePath()
        #print self.logLines[self.index-1].attributes
        #NEW FORMAT..
        #imageType = (self.logLines[self.index-1].data['SampleType'])
        #imageType = (self.logLines[self.index-1].getValue("SMPL_TYPE"))
        
        print imageType
        
        Logger.log(self.name, "INDEX: " + str(self.index))
        #if (imageType == "BUFFER"):
        if (imageType == '0'): #Buffer
            Logger.log(self.name, "BUFFER")
            self.bufferWorker.send("datFile")
            self.bufferWorker.send_pyobj(self.datFiles[self.datIndex-1])
            Logger.log(self.name, "sent DatFile to WorkerBuffer")
        if (imageType == '1'): #Static_image
            Logger.log(self.name, "STATIC IMAGE")
            self.sampleWorker.send("sample")
            self.sampleWorker.send_pyobj(self.datFiles[self.datIndex-1])
            Logger.log(self.name, "Sent DatFile to WorkerStaticImage")
            
            self.rollingAverageWorker.send("sample")
            self.rollingAverageWorker.send_pyobj(self.datFiles[self.datIndex-1])
            Logger.log(self.name, "Sent DatFile to WorkerRollingImage")


    def run(self):   
        print "in run"                    
        #epics.camonitor("13PIL1:cam1:ArrayCounter_RBV", callback=self.imageTaken)
        #epics.camonitor("13SIM1:TIFF1:FilePath_RBV", callback=self.userChange)
 
        try:
            while True:
                self.imageTaken()
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
                    Logger.log(self.name, "IndexError - trying to read last line from logfile")
                    pass
                                
                v.close()
            except IOError:
                Logger.log(self.name, "IOERROR - trying to read last line from logfile")
                Logger.log(self.name, self.logFile)
                time.sleep(0.2)
                pass
            
        
    def getDatFile(self):
        _pass = 0
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
                datFile = (self.datFileLocation + dat)  
                self.datFiles.append(DatFile.DatFile(datFile))
                self.datIndex = self.datIndex + 1
                Logger.log(self.name, "INDEX DATFILES: " + str(self.datIndex))               
                noDatFile = False
            except IOError:
                if (_pass > 3):
                    print "dunno doesnt exist ?"
                    _pass = 0
                    #self.index = self.index - 1
                    break


                Logger.log(self.name, "IOERROR - trying to open latest datfile")
                Logger.log(self.name, "DATFILE - " + str(datFile))


                time.sleep(0.05)
                _pass = _pass + 1



if __name__ == "__main__":
    engine = Engine()
    foo = 1
    engine.userChange("/mnt/images/data/Cycle_2012_1/Melton_4615/")
    engine.run()
