###BASH start stop
#screen -dmS "engine" "./engine.py"


import logging
import sys
import time
import epics
import os

import zmq
import yaml

from threading import Thread

from Core.EngineFunctions import getString as getString
from Core.EngineFunctions import testStringChange as testStringChange
from Core.EngineFunctions import createFolderStructure as createFolderStructure
from Core.RootName import changeInRootName

from Core import LogWatcher
from Core import LogLine
from Core import DatFile


class Engine():
    """
    .. codeauthor:: Jack Dwyer <jackjack.dwyer@gmail.com>
    Is the goto man for controlling the sequence of events that will occur after a datFile has been created
    
    """
    def __init__(self, configuration):
        self.name = "Engine"
        self.logger = None
        self.setLoggingDetails()
        
        #Instantiate class variables
        self.first = True #For catching index error
        self.rootDirectory = None
        self.user = None
        self.logLines = []
        self.needBuffer = True
        
        # Object that will be watching the LiveLogFile
        self.logWatcher = LogWatcher.LogWatcher()

        
        #SET Correctly in newUser
        self.liveLog = None
        self.datFileLocation = None
        
        self.previousUser = None #Used to compare current user against new user (to stop if users click the pv etc)
        self.previousExperiment = None
        self.workers = None

        #Read all configuration settings
        self.setConfiguration(configuration)

        #ZMQ Class Variables
        self.zmqContext = zmq.Context()
        self.requestBuffer = None

        #Instantiate all workers, get them all ready to push out into their own thread and connected up
        self.instanceWorkerDict = self.instantiateWorkers(self.workers)
        #Connect up workers
        self.connectWorkers(self.instanceWorkerDict)    
    
    def setConfiguration(self, configuration):
        """Reads the default configuration file that is passed at object creation 
        The configuration stores the Workers that need to be loaded, whether an Experiment name is being used
        The Absolute location of the datFiles.
        Any PV's that need to be watched
    
        Args:
            Configuration (file): A YAML config file
          
        Returns:
           Nothing
           
        Sets class Variables:
            | self.rootDirectory = The absolute location of the experiments as mounted on the local machine.
            | self.userChangePV = The FullPath PV from epics to watch for user/experiment change over.
            | self.experimentFolderOn = Switch if they experiment folders are being used.
            | self.workrs = List of all workers that need to be instantiated.
          
        Raises:
           IOError: When it is unable to find the configuration
        """    
        try:
            stream = file(configuration, 'r') 
        except IOError:
            logging.critical(self.name, "Unable to find configuration file (config.yaml, in current directory), exiting.")
            sys.exit
        
        config = yaml.load(stream)
        self.rootDirectory = config.get('RootDirectory')
        self.userChangePV = config.get('UserChangePV')
        self.experimentFolderOn = config.get('ExperimentFolderOn')
        
        print self.experimentFolderOn
        
        self.workers = config.get('workers')

    def instantiateWorkers(self, workers):
        """Instantiates each worker as specified by the Configuration 
        
        Args:
            Workers: A list of string names of each worker
            
        Returns:
            instanceDict: A dictionary of Key (Worker Name String): Value (Instantiated Worker Object)
        """
        self.logger.info("Instantiating all workers")
        instanceDict = {}
        for worker in workers:
            im = __import__('Workers.'+worker, globals(), locals(), [worker])
            v = getattr(im, worker)
            x = v()
            instanceDict[worker] = x
        return instanceDict

    def connectWorkers(self, instanceDict):
        """
        Connects all Workers to required ZMQ sockets
        Loads each worker into a Daemon Thread
        Uses Push for all workers
        PUB/SUB for WorkerDB
        REQ/REP for WorkerBufferAverage
        
        
        Args:
            instanceDict (dictionary): Dictionary created from instantiateWorkers
        
        Returns:
            Nothing
        
        Sets Class Variables:
            | self.connectedWorkers = Dictionary - key, Worker(string): push port(string)
        
        
        """
        
        pushPort = 2000
        pubPort = 1998
        bufferRequestPort = 1999
        
        #Actual Worker Threads
        workerThreads = {}
        #Which worker, and which port are they on
        workerPortLocation = {}
        self.connectedWorkers = {}

        #Start up a dictionary of threads, so we know where all the workers are        
        for worker in instanceDict:
            if (worker == "WorkerBufferAverage"):
                workerThreads[worker] = Thread(target=instanceDict[worker].connect, args=(pushPort, pubPort, bufferRequestPort))
                workerPortLocation[worker] = pushPort
                self.requestBuffer = self.zmqContext.socket(zmq.REQ)
                self.requestBuffer.connect("tcp://127.0.0.1:"+str(bufferRequestPort))
                pushPort = pushPort + 1
            else:
                workerThreads[worker] = Thread(target=instanceDict[worker].connect, args=(pushPort, pubPort,))                            
                workerPortLocation[worker] = pushPort #So we know where to send commands
                pushPort = pushPort + 1
            
        #Set all workers as Daemon threads (so they all die when we close the application)
        for workerThread in workerThreads:
            workerThreads[workerThread].setDaemon(True)
            
        #Start all the threads
        for workerThread in workerThreads:
            workerThreads[workerThread].start()
            time.sleep(0.1) #short pause to let them properly bind/connect their ports
            
        #Set up ZMQ context for each worker
        for worker in workerPortLocation:
            workerPortLocation[worker]
            self.connectedWorkers[worker] = self.zmqContext.socket(zmq.PUSH)
        
        #connect workers to the engine
        for worker in self.connectedWorkers:
            self.connectedWorkers[worker].connect("tcp://127.0.0.1:"+str(workerPortLocation[worker]))

        self.logger.info("All Workers connected and ready")


    # Event Watching
    def setUserWatcher(self):
        """
        Sets up a epics.camonitor against the PV set by the configuration file
        
        Callback:
            setUser()
        """
        
        epics.camonitor(self.userChangePV, callback=self.setUser)
        
    def watchForLogLines(self, logLocation):
        """
        Creates an object for watching the logfile that callsback when ever a new line has been written
        
        Callback:
            lineCreated()
        
        """      
        self.logWatcher.setLocation(logLocation)
        self.logWatcher.setCallback(self.lineCreated)
        self.logWatcher.watch()
        
    def killLogWatcher(self):
        """
        Kills Log Watcher Object
        """
        self.logWatcher.kill()



        
    def setUser(self, char_value, **kw):
        """
        | Sets the User for the Engine, and all workers.
        | Is called when the PV changes
        | Checks new user value against previous user
        | If matching values, nothing occurs
        | Calls newUser(user) if it is a new user
        
        Args:
            char_value (string): String value of the PV, should be the full path to the image locations relative to epics
            **kw (dict): remaining values returned from epics
            
        """
        self.logger.info("User Change Event")
        
        #user = getUser(char_value)
        
        if (self.experimentFolderOn):
            print "Experiment folder on"
            experiment = getString(char_value, -2)
            user = getString(char_value, -3)
            
            print "EXPERIMENT : %s" % experiment
            print "USER : %s" % user

            #Test user change
            if (testStringChange(user, self.previousUser)):
                print "USER CHANGE, SO YES experiment CHANGE \nRUN user.change with experiment!"
                self.previousUser = user
                self.previousExperiment = experiment
                self.newUser1()

            else:
                print "NO USER CHANAGE"
                
                print "BETTER CHECK IF USER CHANGED!"
                if (testStringChange(experiment, self.previousExperiment)):
                    print "EXPERUIMENT CHANGE!"
                    self.previousExperiment = experiment
                    self.newExperiment()
                else:
                    print "Nothing changed, user nor experiment"
                    pass
            

        #experiment filder is off, onlty just againse user
        else:
            print "exerpimetn folder off, on;y check user"
            user = getString(char_value, -2)
            print "USER: %s" % user
            
            if testStringChange(user, self.previousUser):
                print "USER HAS CHANGED, run new user"
                self.previousUser = user
                self.newUser1()

            else:
                print "NO USER CHANGE DO NOTHING"
                pass
            
                
                
                
        """    
        else:
            user = getUser(char_value, -2)
            if (testUserChange(user, self.previousUser)):
                self.previousUser = user
                self.newUser(user)
            else:
                pass
        """
        
    def newExperiment(self):
        print "function new experiment"
        
    def newUser1(self):
        print "function new user"
        
    def newUser(self, user):
        """
        New User has been found, need to communicate to myself and all workers the new details
        A new Database is created
        And the engine commences watching the logfile.
        
        Args:
            user (string): string value of the user
         
        """
        
        
        self.logger.info("New User Requested")
        #Reset class variables for controlling logic and data
        self.first = True
        self.logLines = []
        self.needBuffer = True
        
        self.user = user
        self.liveLog = self.rootDirectory + "/" + self.user + "/images/livelogfile.log"
        self.datFileLocation = self.rootDirectory + "/" + self.user + "/raw_dat/"
        
        #Generate Directory Structure
        createFolderStructure(self.rootDirectory, self.user)
        self.logger.info("Directory Structure Created")
        
        #Update all workers
        self.sendCommand({"command":"update_user", "user":self.user})
        self.sendCommand({"command":"absolute_directory","absolute_directory":self.rootDirectory + "/" + self.user})
        
        
        
        
        self.createDB()
        
        #Start waiting for log to appear
        self.watchForLogLines(self.liveLog) # Start waiting for the Log


    def run(self):
        """
        Starts the epics watcher for user change
        Keeps on running as the main thread
        """ 
        self.setUserWatcher() #Start epics call back
              
        while True:
            #Keep the script running
            time.sleep(0.1)
        
 
 
 
 
    def lineCreated(self, line, **kw):
        """
        | Here we parse the logline for the Image Location
        | it Preliminarily checks against the image type for weather it needs to bother looking for it or not 
        | Calls processDat if we care for the datFile
        | sends the logline to be written out to the database
        
        Args:
            line (string): returned latest line from call back
            **kw (dictionary): any more remaining values
        """
        
        latestLine = LogLine.LogLine(line)
        self.logLines.append(latestLine)
        
        #Send off line to be written to db
        self.sendLogLine(latestLine)
        
        if (latestLine.getValue("SampleType") == "0" or latestLine.getValue("SampleType") == "1"):
            datFile = self.getDatFile(latestLine.getValue("ImageLocation"))
            if (datFile):
                self.processDat(latestLine, datFile)
        else:
            self.logger.info("Hey, it's a sample type I just don't care for!")
   
   
    def getDatFile(self, fullPath):
        """
        | Called from lineCreated, is called if we want the datFile from the log line
        | It looks in the location created from the configuration file for the corresponding datFile
        | Times out after 3seconds and passes
        
        Args:
            fullPath (String): Absolute location of the datFile from the LogLine
            
        Returns:
            | datFile object created from the static image
            | or, returns False if nothing is found
        
        """
        imageName = os.path.basename(fullPath)
        imageName = os.path.splitext(imageName)[0]
        datFileName = imageName + ".dat"

        
        time.sleep(0.1) #have a little snooze to make sure the image has been written
        self.logger.info("Looking for DatFile %s" % datFileName)
   
        startTime = time.time()
        while not os.path.isfile(self.datFileLocation + datFileName):
            self.logger.info("Waiting for the %s" % datFileName)
            time.sleep(0.5)
            if (time.time() - startTime > 3.0):
                self.logger.critical("DatFile: %s - could not be found - SKIPPING" % datFileName)
                return False
        
        datFile = DatFile.DatFile(self.datFileLocation +  datFileName)
        self.logger.info("DatFile: %s - has been found" % datFileName)
        return datFile
   
   
    def processDat(self, logLine, datFile):
        """
        
        | Here we will decide how to process the datFile
        | Sample Types:
        | 6 - Water
        | 0 - Buffer
        | 1 - Static Sample
        
        | Sample type of DatFile is determined by the logline.  We only currently care for 0 (buffer), or 1 (static Sample)
        | Is sample is a buffer, it needs to be passed to WorkerBufferAverage to be processed
        | If it is a sample it is passed to all workers to be processed by them if they want
        
        We check if the Workers need an AveragedBuffer which we then can request from WorkerBufferAverage
        We check for a rootname change indicating a new sample which may or may not require a new buffer average
        
        Args:
            logLine (LogLine Object): Latest Logline
            datFile (datFile Object): Corresponding DatFile from LogLine
            
        Raises:
            IndexError: Raised only on first pass, as we need the current user to check againse the previous user
        
        """
        
        
        try:
            if (changeInRootName(os.path.basename(self.logLines[-1].getValue("ImageLocation")), os.path.basename(self.logLines[-2].getValue("ImageLocation")))):
                self.logger.info("There has been a change in the root name")
                
                self.sendCommand({"command":"root_name_change"})
                
                
                if (logLine.getValue("SampleType") == "0"):
                    self.logger.info("New Buffer!")
                    self.needBuffer = True
                    self.sendCommand({"command":"new_buffer"})
                    self.sendCommand({"command":"buffer", "buffer":datFile})
                
                
                if (logLine.getValue("SampleType") == "1"):
                    if (self.needBuffer):
                        averagedBuffer = self.requestAveragedBuffer()
                        print "AVERAGED BUFFER"
                        print averagedBuffer
                        if (averagedBuffer):
                            self.sendCommand({"command":"averaged_buffer", "averaged_buffer":averagedBuffer})
                            self.needBuffer = False
                            self.sendCommand({"command":"static_image", "static_image":datFile})
                            
                        else:
                            self.sendCommand({"command":"static_image", "static_image":datFile})

                    else:
                        self.logger.info("So lets average with current buffer!")
                
            else:
                self.logger.info("No change in root name fellas")
                
                if (logLine.getValue("SampleType") == "0"):
                    self.sendCommand({"command":"buffer", "buffer":datFile})

                if (logLine.getValue("SampleType") == "1"):
                    if (self.needBuffer):
                        averagedBuffer = self.requestAveragedBuffer()
                        print averagedBuffer
                        if (averagedBuffer):
                            self.sendCommand({"command":"averaged_buffer", "averaged_buffer":averagedBuffer})
                            self.needBuffer = False
                            self.sendCommand({"command":"static_image", "static_image":datFile})

                        else:
                            self.logger.critical("No averaged Buffer returned unable to perform subtraction")
                    else:
                        self.sendCommand({"command":"static_image", "static_image":datFile})
                    


       
        except IndexError:
            if (self.first):
                self.first = False
            else:
                self.logger.info("INDEX ERROR - Should only occur on first pass!")
                   



    
    def cli(self):
        try:
            while True:
                print "exit - to exit"
                print "workers - sends test command out to find workers that are alive"
                print "variables - returns all the class variables of each worker"
                request = raw_input(">> ")
                if (request == "exit"):
                    self.exit()
                if (request == "workers"):
                    self.test()
                if (request == "variables"):
                    self.sendCommand({"command":"get_variables"})
                
                
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass

    #Generic Methods
    def sendCommand(self, command):
        """
        Sends a structed Dictionary command to all connected Workers
        
        Args:
            command (Dictionary): requested command to be sent
        
        """
        if (type(command) is dict):
            for worker in self.connectedWorkers:
                self.connectedWorkers[worker].send_pyobj(command)
        else:
            self.logger.critical("Incorrect Command datatype, must send a dictionary")

    def sendLogLine(self, line):
        """
        Sends the pass logline to the WorkerDB to be written out to the database
        
        Args:
            line (LogLine object): LogLine object that you want to write to the DB
        """
        self.connectedWorkers['WorkerDB'].send_pyobj({"command":"log_line", "line":line})
        
    def createDB(self):
        """
        Create the specified database for the new user
        """
        
        self.connectedWorkers['WorkerDB'].send_pyobj({"command":"createDB"})
        
    def requestAveragedBuffer(self):
        """
        Request from the WorkerBufferAverage for the current averaged buffer
        
        Returns:
            Averaged Buffer List
        """
        
        self.requestBuffer.send("request_buffer")
        buffer = self.requestBuffer.recv_pyobj()
        return buffer
    
    
    def test(self):
        self.sendCommand({'command':"test"})
        time.sleep(0.1)
        
    def exit(self):
        """
        Properly shuts down all the workers
        """
        self.sendCommand({"command":"shut_down"})
        time.sleep(0.1)
        sys.exit()
        
        
    def setLoggingDetails(self):
        """
        Current generic logging setup using the python logging module
        """
        LOG_FILENAME = 'logs/'+self.name+'.log'
        FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,format=FORMAT)
        
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        console.setFormatter(formatter)
        logging.getLogger(self.name).addHandler(console)
        
        self.logger = logging.getLogger(self.name)
        self.logger.info("\nLOGGING STARTED")


if __name__ == "__main__":
    eng = Engine("settings.conf")
    eng.run()



