"""
Jack Dwyer
26/04/2012

Engine v0.3
- Loads all default workes

"""



import yaml
import epics
import time
import zmq
import sys
import os
from Core import DatFile
from Core import LogLine
from Core.Logger import logger
from Core import DirectoryCreator
#import MySQLdb as mysql
from Core.RootName import changeInRootName

from threading import Thread

from Workers import WorkerBufferAverage
from Workers import WorkerDB
from Workers import WorkerRollingAverageSubtraction
from Workers import WorkerStaticImage

from Workers import WorkerEMBLmolSize




class Engine():
    """
    Starts Buffer Average worker first so buffer average can bind to the correct port
    """
    
    def __init__(self, configuration):
        self.name = "Engine"
        
        #Get Configuration settings
        try:
            stream = file(configuration, 'r') 
        except IOError:
            logger(self.name, "Unable to find configuration file (config.yaml, in current directory), exiting.")
            exit()
            
        self.config = yaml.load(stream)
        
        self.rootDirectory = self.config['RootDirectory']
        self.imageTakenPV = self.config['ImageTakenPV']
        self.userChangePV = self.config['UserChangePV']
        self.relativeLogFileLocation = self.config['RelativeLogFileLocation']
        self.experimentName = self.config['ExperimentName']
        

        
        self.lineIndex = 0        
        self.log = ""

        self.latestLogLine = ""
        self.logLines = []
        self.lines = []
        #Will hold the latest created dat file
        self.datFile = ""
        
        self.needBuffer = True #Switch for requesting a new buffer
        self.aveBuffer = "" #For holding the latest averaged buffer
        
        self.absoluteLocation = "" #Properly Created with setuser, it is a concatenation of rootDirectory & user
        self.logLocation = "" #Properly set in setUser also
        self.datFileLocation = "" #Properly set in setUser
        
        
        
        

        
        logger(self.name, "Engine Started")
        
        #ZeroMQ setup stuff
        self.context = zmq.Context()
        
        #Current User
        self.user = ""
      
        #Default workers
        self.bufferAverage = WorkerBufferAverage.WorkerBufferAverage()
        self.staticImage = WorkerStaticImage.WorkerStaticImage()
        self.rollingAverageSubtraction = WorkerRollingAverageSubtraction.WorkerRollingAverageSubtraction()
        self.dbWorker = WorkerDB.WorkerDB()
        self.WorkerEMBLmolSize = WorkerEMBLmolSize.WorkerEMBLmolSize()
        
        #Connect Up all Workers, and have them ready
        self.bufferRequest = self.context.socket(zmq.REQ)
        self.bufferRequest.connect("tcp://127.0.0.1:5000")
        logger(self.name, "Connected -> BufferRequest")

        self.bufferPush = self.context.socket(zmq.PUSH)
        self.bufferPush.bind("tcp://127.0.0.1:5001")
        logger(self.name, "Binded -> BufferPush")

        self.staticPush = self.context.socket(zmq.PUSH)
        self.staticPush.connect("tcp://127.0.0.1:5002")
        logger(self.name, "Binded -> StaticPush")
        
        
        self.dbPush = self.context.socket(zmq.PUSH)
        self.dbPush.connect("tcp://127.0.0.1:5003")
        logger(self.name, "Binded -> dbPush")
     

        self.rollingPush = self.context.socket(zmq.PUSH)
        self.rollingPush.bind("tcp://127.0.0.1:5004")
        logger(self.name, "Binded -> RollingPush")
        
        self.EMBLmolSizePush = self.context.socket(zmq.PUSH)
        self.EMBLmolSizePush.connect("tcp://127.0.0.1:5005")
        logger(self.name, "Binded -> EMBL1Push")

        time.sleep(0.5)
        

        
        time.sleep(0.1)

        
        bufferThread = Thread(target=self.bufferAverage.connect, args=(5001, 5003, 5000,))
        bufferThread.setDaemon(True)
        bufferThread.start()  
        
        time.sleep(0.1)
        
        EMBL1Thread = Thread(target=self.WorkerEMBLmolSize.connect, args=(5005, 5003, ))
        EMBL1Thread.setDaemon(True)
        EMBL1Thread.start()
    
        
        staticImageThread = Thread(target=self.staticImage.connect, args=(5002, 5003, 5005, ))
        staticImageThread.setDaemon(True)
        staticImageThread.start()
        
        time.sleep(0.1)

        
        rollingAverageThread = Thread(target=self.rollingAverageSubtraction.connect, args=(5004, 5003,))
        rollingAverageThread.setDaemon(True)
        rollingAverageThread.start()
        
        time.sleep(0.1)

        
        dbThread = Thread(target=self.dbWorker.connect, args=(5003, ))
        dbThread.setDaemon(True)
        dbThread.start()

        time.sleep(0.5)
        
        self.setRootDirectory()
        self.watchForUserChangeOver()
        self.watchForImage() 
        
        time.sleep(0.1) 
        self.logLocation = self.absoluteLocation + self.relativeLogFileLocation
        self.datFileLocation = self.absoluteLocation + "/raw_dat/"

        logger(self.name, "All Workers ready")
        
        self.dbPush.send("test")


        #TODO: REMOVE this, shouldnt really be set here
        self.absoluteLocation = self.rootDirectory + self.user 
        self.logLocation = self.absoluteLocation + self.relativeLogFileLocation
        self.datFileLocation = self.absoluteLocation + "/raw_dat/"


        #Start this thread last
        cliThread = Thread(target=self.cli())
        cliThread.setDaemon(True)
        cliThread.start()
        
        #self.live()
        
        
    def live(self):
        while True:
            self.imageTaken()
            time.sleep(1)
    
                
    def setRootDirectory(self):
        self.sendCommand("rootDirectory")
        self.sendCommand(self.rootDirectory)
       
       
        
       
    #ENGINE Specific stuff -
    
    """
    Epics Monitoring
    """
    def watchForUserChangeOver(self):
        epics.camonitor(self.userChangePV, callback=self.setUser)
            
    def watchForImage(self):
        epics.camonitor(self.imageTakenPV, callback=self.imageTaken)
         
    """
    Engine Functions
    - Reading log, creating log objects that can be passed around
    - Getting Image/Dat File - same again creating them into objects to be thrown around
    - 
    """    
       
    def imageTaken(self, char_value, **kw):
        print "imageTaken()"
        self.readLatestLogLine()
    
    
    def readLatestLogLine(self):
        if not (self.log):
            start_time = time.time()
            logger(self.name, "Opening Log File")
            while not (self.log):
                if ((time.time() - start_time) == 30.0):
                    logger(self.name, "Error: can not open log file at location: " + self.logLocation)
                    logger(self.name, "Shutting down")
                else:
                    time.sleep(0.1)
                    self.log = open(self.logLocation, 'r')
    
        numLines = len(self.log.readlines())
        #if its behind
        while (self.lineIndex < numLines):
            logger(self.name, "Behind current logFile/experiment -- TURBO MODE ENABLED")
            for i in (len(self.log.readlines()) - self.lineIndex ):
                self.latestLogLine = LogLine.LogLine(self.log.readlines()[i])
                self.logLines.append(self.latestLogLine)
                imageFileName = os.path.basename(self.latestLogLine.getValue("ImageLocation"))
                self.sendLogLine(self.latestLogLine)
                self.getImage(imageFileName)
                self.lineIndex = self.lineIndex + 1
        
        while (self.lineIndex > numLines):
            logger(self.name, "Ahead of current log lines, sleeping for 0.5seconds")
            time.sleep(0.5)
            continue
            
        if (self.lineIndex == numLines):
            self.latestLogLine = LogLine.LogLine(self.log.readlines()[i])
            self.logLines.append(self.latestLogLine)
            imageFileName = os.path.basename(self.latestLogLine.getValue("ImageLocation"))
            self.sendLogLine(self.latestLogLine)
            self.getImage(imageFileName)
            self.lineIndex = self.lineIndex + 1
        else:
            logger(self.name, "self.lineIndex some how failed.")
                
    """    
    def readLatestLogLine2(self, image_name):
        start_time = time.time()
    
        if not (self.logLine):
            logger(self.name, "Opening Log File")
            while start_time < 30:
                time.sleep(0.2)
                self.logLine = open(self.logLocation, 'r')
            logger(self.name, "ERROR: can not open log file at location: %s - Shutting down", self.logLocation)
            sys.exit()
            
        while True:
            if (self.index < len(self.log.readlines())):
                logger(self.name, "Behind Current logFile - Need to catch up! Turbo mode enabled.")
                for i in range(self.index - (len(self.log.readlines()))):
                    print i
        
        
        #Test if above the current engines index
            if (self.index > len(self.log.readlines())):
                logger(self.name, "Ahead of current log line, sleeping for 0.5seconds")
                time.sleep(0.5)
                continue
        
        print "Dropping out of readLastLogline_2"
        print self.index
        
    
    
    
        
    def readLatestLogLine(self, image_name):
        print "read lastest log line"
        start_time = time.time() 

        while True:
            try:
                print "trying to open log file"
                logFile = open(self.logLocation, "r")
                time.sleep(0.5)
                print "slept for 0.5 seconds"
                if time.time()-start_time > 10.0: 
                    logger(self.name, "Timeout waiting for: LOG FILE")
                    logger(self.name, "Shutting down...")
                    sys.exit()      
            	
                self.latestLogLine = logFile.readlines()[-1]
                tempLogLine = LogLine.LogLine(self.latestLogLine)
                if(tempLogLine.getValue('ImageLocation') != image_name):
                    print("Image doesnt match latest line")
                    continue
                self.logLines.append(tempLogLine)
                self.index = self.index + 1
                logger(self.name, "LogLine read : %s" % self.latestLogLine)
                self.sendLogLine(LogLine.LogLine(self.latestLogLine))
                
                #Get image location
                imageFileName = os.path.basename(self.logLines[-1].getValue("ImageLocation"))
                logger(self.name, "Image : %s" % imageFileName)
                self.getImage(imageFileName)
                return
            except KeyboardInterrupt:
                logger(self.name, "Error: Unable to read Log File")
                return False
                
    """
    def getImage(self, imageFileName):
        start_time = time.time() 
        #Get jsut the image/dat nme without extension
        imageName = os.path.splitext(imageFileName)[0]
    
        #add the .dat to image name, so it knows what its looking for
        imageName = imageName + ".dat"
        time.sleep(0.1) #Give it a little break to write out the dat file
        
        logger(self.name, "getImage called, with %s" % imageName) 
        

        
        while not os.path.isfile(self.datFileLocation + imageName):
            logger(self.name, "Waiting for: %s" % imageName)
            time.sleep(0.5)
            if time.time()-start_time > 3.0: 
                logger(self.name, "Timeout waiting for: %s" % imageName)
                return            
        
        logger(self.name, "Retrieved: %s" % imageName)
        self.datFile = DatFile.DatFile(self.datFileLocation +  imageName)
        
        self.processDatFile(self.datFile, self.logLines[-1])
        
        
        
    def processDatFile(self, datFile, logLine):
        """
        Sample Types:
        6 - Water
        0 - Buffer
        1 - Static Sample
        """
        print logLine.getValue('SampleType')
        
        try:
            if (changeInRootName(os.path.basename(self.logLines[-1].getValue("ImageLocation")), os.path.basename(self.logLines[-2].getValue("ImageLocation")))):
                
                logger(self.name, "Change in root names")
                
                if (logLine.getValue("SampleType") == "0"):
                    self.sendCommand("new_buffer")
                    self.needBuffer = True
                    #logger(self.name, "Buffer Received")
                    self.sendBuffer(datFile)
    
                if (logLine.getValue("SampleType") == "1"):
                    
                    if (self.needBuffer):
                        logger(self.name, "Need A Buffer")
                        if (self.requestAverageBuffer()):
                            self.sendAverageBuffer(self.aveBuffer)
                            self.needBuffer = False
                            self.sendImage(datFile)
                        else:
                            logger(self.name, "Request for averaged buffer failed, subtraction unable to occurr")
                    else:
                        self.sendImage(datFile)
                        logger(self.name, "Just Image Sent")
                        
    
                
            else:
                logger(self.name, "NO CHANGE in root names")
    
                if (logLine.getValue("SampleType") == "0"):
                    self.sendBuffer(datFile)
                    logger(self.name, "BUFFER SENT")
    
                if (logLine.getValue("SampleType") == "1"):
                    
                    if (self.needBuffer):
                        logger(self.name, "Need A Buffer")

                        if (self.requestAverageBuffer()):
                            self.sendAverageBuffer(self.aveBuffer)
                            self.needBuffer = False
                            self.sendImage(datFile)
                        else:
                            logger(self.name, "Request for averaged buffer failed, can not subtract datfile")
                        
                    else:
                        self.sendImage(datFile)
                        logger(self.name, "No buffer needed")

                        #send just the image
                        


        except(IndexError):
            logger(self.name, "index error, must be first pass")
 
        
    def sentTest(self):
        self.sendCommand("update_user")   
        self.sendCommand("jack")
        
        
        
    def getUser(self, path):
        """Splits file path, and returns only user"""
        user = path.split("/")
        user = filter(None, user) #needed to remove the none characters from the array
        return user[-2] #currently the user_epn is the last object in the list
    
    def setUser(self, char_value = False, **kw):
        #TODO remove this, need another way to pass user directly
        if not (char_value): #needed for cli, though my kill engine, if user monitor doesnt return a valid value
            char_value = raw_input("Enter User: ")
        
        self.user = self.getUser(char_value) #get new user
        logger(self.name, "User Changed -> " + str(self.user))
        
        self.sendCommand("update_user")
        self.sendCommand(self.user)
        
        self.generateDirectoryStructure()
        
        
        self.absoluteLocation = self.rootDirectory + self.user 
        self.logLocation = self.absoluteLocation + self.relativeLogFileLocation
        self.datFileLocation = self.absoluteLocation + "/raw_dat/"
        
        #Clear out some variables to be ready for the new user
        self.lineIndex = 0
        self.log = ""
    
        self.sendCommand("absolute_location")
        self.sendCommand(self.absoluteLocation)

       
    def bufferTaken(self):
        t = raw_input("Enter a Test String (will be sent as an object) > ")
        self.sendBuffer(t)
    
    #Engine Control       
    def requestAverageBuffer(self):
        self.bufferRequest.send("request_buffer")
        self.aveBuffer = self.bufferRequest.recv_pyobj()
        print "SELF average Buffer"
        print self.aveBuffer
        if (self.aveBuffer == "no_buffer"):
            return False
        else:
            return True  	

    def returnUser(self):
        logger(self.name, "Current User : " + self.user)
        self.sendCommand("getUser")
    
    
    def cli(self):        
        self.helpMenu() #Prints out command menu
        while True:
            time.sleep(0.1) #TODO: fixing printing output. - This is a quick fix to give enough time for all threads and workers
                            #to print/log out there data
            command = str(raw_input(">> "))
            if (command == "exit"):
                self.exitEngine()
            if (command == "help"):
                self.helpMenu()
            if not hasattr(self, command):
                print "%s is not a valid command" % command
                print "Use 'help' to list all commands"
            else:
                getattr(self, command)()
        
    def helpMenu(self):
        print '%30s' % "==================== Commands ========="
        formatting  = '%30s %10s %1s'
        print formatting % ("help", '--', "Prints help menu"+"\n"),
        print formatting % ("testPush", '--', "Runs push test across workers"+"\n"),
        print formatting % ("testRequest", '--', "Runs request test against BufferAverage" +"\n"),
        print formatting % ("setUser",'--', "Set Current User from Engine"+"\n"),
        print formatting % ("returnUser",'--', "Returns Current User from Engine and all workers"+"\n"),
        print formatting % ("imageTaken", '--', "Force Image Taken Routine")
        print formatting % ("requestAverageBuffer", "--", "Request for latest average buffer")
        print formatting % ("epicSetUser", '--', "Force Epics to have a new user")
        print formatting % ("exit", '--', "Exit Engine")


        
    def exitEngine(self):
        self.sendCommand("exit")
        time.sleep(0.2)
        logger(self.name, "Exiting")
        sys.exit()

        
        
    #########
    # Helper functions
    def sendCommand(self, command):
        self.dbPush.send(command)
        self.staticPush.send(command)
        self.bufferPush.send(command)
        self.rollingPush.send(command)
        self.EMBLmolSizePush.send(command)

    def testImageTaken(self):
        self.imageTaken()
        
    def sendImage(self, datFile):
        self.staticPush.send("static_image")
        self.staticPush.send_pyobj(datFile)
        self.rollingPush.send("static_image")
        self.rollingPush.send_pyobj(datFile)
    
    def sendAverageBuffer(self, datFile):
        self.staticPush.send("average_buffer")
        self.staticPush.send_pyobj(datFile)
        self.rollingPush.send("average_buffer")
        self.rollingPush.send_pyobj(datFile)
        
    def sendBuffer(self, datFile):
        self.bufferPush.send("buffer")
        self.bufferPush.send_pyobj(self.datFile)
        
    def sendLogLine(self, logLine):
        self.dbPush.send("log_line")
        self.dbPush.send_pyobj(logLine)
        
    def generateDirectoryStructure(self):
        dirCreator = DirectoryCreator.DirectoryCreator(self.rootDirectory)
        dirCreator.createFolderStructure(self.user, "experiment1")
        logger(self.name, "Generated Directory Structure")
                
        
    #For Testing    
    def testPush(self):
        command = raw_input("Enter Test String (to be pushed) > ")
        self.sendCommand("testPush")
        self.sendCommand(command)
        
    def testRequest(self):
        self.bufferRequest.send("test")
        test = self.bufferRequest.recv_pyobj()
        logger(self.name, "RESPONSE RECIEVED -> " + test)
        
    def epicSetUser(self):
        user = raw_input("Enter new user > ")
        epics.caput("13SIM1:TIFF1:FilePath", "/some/where/on/the/" + user + bytearray("\0x00"*256))
        
    def epicImageTaken(self):
        epics.caput("13SIM1:cam1:NumImages.VAL", 1, wait=True)

    def getLogLoc(self):
        print self.logLocation    
    
    def getVariables(self):
        print "Absolute Location: ", str(self.absoluteLocation)
        print "LogLocation: ", str(self.logLocation)
        print "DatFile Location: ", str(self.datFileLocation)
        print "SELF-Index: ", str(self.index)

    def forceCommand(self):
        command = raw_input("Enter Command >>")
        self.sendCommand(command)

        

if __name__ == "__main__":
    engine = Engine("config.yaml")
    #engine.testPush()
    #engine.testRequest()
    #engine.watchForChangeOver()
