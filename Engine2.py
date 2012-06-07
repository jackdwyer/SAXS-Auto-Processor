"""
Engine using standard configparse over pyYaml

Jack Dwyer

TODO import logging and use that across all workers/core/engine etc
"""
import logging
import sys
import time
import epics

import zmq
import yaml

from threading import Thread

from Core.EngineFunctions import getUser as getUser
from Core.EngineFunctions import testUserChange as testUserChange
from Core.EngineFunctions import createFolderStructure as createFolderStructure


#from Workers import Worker



class Engine2():
    def __init__(self, configuration):
        #Set up the Logger
        self.name = "Engine"
        self.logger = None
        self.setLoggingDetails()
        
        #Instantiate class variables
        self.rootDirectory = None
        
        #SET Correctly in newUser
        self.liveLog = None
        self.datFileLocation = None
        
        self.previousUser = None #Used to compare current user against new user (to stop if users click the pv etc)
        
        self.workers = None

        #Read all configuration settings
        self.setConfiguration(configuration)

        #ZMQ Class Variables
        self.zmqContext = zmq.Context()

        #Instantiate all workers, get them all ready to push out into their own thread and connected up
        self.instanceWorkerList = self.instantiateWorkers(self.workers)
        #Connect up workers
        self.connectWorkers(self.instanceWorkerList)
    
    
    def setConfiguration(self, configuration):
        """ Default configuration is settings.conf """
        try:
            stream = file(configuration, 'r') 
        except IOError:
            logging.critical(self.name, "Unable to find configuration file (config.yaml, in current directory), exiting.")
            sys.exit
        
        config = yaml.load(stream)
        self.rootDirectory = config.get('RootDirectory')
        self.userChangePV = config.get('UserChangePV')
        
        self.workers = config.get('workers')

    def instantiateWorkers(self, workers):
        self.logger.info("Instantiating all workers")
        instanceDict = {}
        """Loads up each worker into their own thread
        sets them to be daemons and starts the thread"""
        for worker in workers:
            im = __import__('Workers_new.'+worker, globals(), locals(), [worker])
            v = getattr(im, worker)
            x = v()
            instanceDict[worker] = x
        return instanceDict

    def connectWorkers(self, instanceList):
        pushPort = 2000
        pubPort = 1999
        
        #Actual Worker Threads
        workerThreads = {}
        #Which worker, and which port are they on
        workerPortLocation = {}
        self.connectedWorkers = {}

        #Start up a dictionary of threads, so we know where all the workers are        
        for worker in instanceList:
            workerThreads[worker] = Thread(target=instanceList[worker].connect, args=(pushPort, pubPort,))                            
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



    def setUserWatcher(self):
        epics.camonitor(self.userChangePV, callback=self.setUser)
        
    def setUser(self, char_value, **kw):
        self.logger.info("User Change Event")

        user = getUser(char_value)
        if (testUserChange(user, self.previousUser)):
            self.previousUser = user
            self.newUser(user)
        else:
            pass
        
    def newUser(self, user):
        self.logger.info("New User Requested")

        self.user = user
        self.liveLog = self.rootDirectory + "/" + self.user + "/images/livelogfile.log"
        self.datFileLocation = self.rootDirectory + "/raw_dat/"
        
        #Generate Directory Structure
        createFolderStructure(self.rootDirectory, self.user)
        self.logger.info("Directory Structure Created")
        
        #Update all workers
        self.sendCommand({"command":"update_user", "user":self.user})
        self.sendCommand({"command":"absolute_directory","absolute_directory":self.rootDirectory + "/" + self.user})


    def run(self):
        self.setUserWatcher() #Start epics call back
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
        for worker in self.connectedWorkers:
            self.connectedWorkers[worker].send_pyobj(command)


    def test(self):
        self.sendCommand({'command':"test"})
        time.sleep(0.1)
        
    def exit(self):
        self.sendCommand({"command":"shut_down"})
        time.sleep(0.1)
        sys.exit()
        
        
    def setLoggingDetails(self):
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
    eng = Engine2("settings.conf")
    eng.run()



