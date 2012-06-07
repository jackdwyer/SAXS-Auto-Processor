"""
Engine using standard configparse over pyYaml

Jack Dwyer

TODO import logging and use that across all workers/core/engine etc
"""
import logging
import sys
import time

import zmq
import yaml

from threading import Thread


#from Workers import Worker



class Engine2():
    def __init__(self, configuration):
        #Set up the Logger
        
        #Instantiate class variables
        self.rootDirectory = None
        self.liveLog = None
        self.datFileLocation = None
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
        self.rootDirectory = config.get('ExperimentDirectory')
        self.workers = config.get('workers')
            

            
    def instantiateWorkers(self, workers):
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
            if (instanceList[worker].getName() == "WorkerDB"):
                workerThreads[worker] = Thread(target=instanceList[worker].connect, args=(pubPort,))                
            else:
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


        

        

    #Generic Methods
    def sendCommand(self, command):
        dicCommand = {'command':command}
        for worker in self.connectedWorkers:
            self.connectedWorkers[worker].send_pyobj(dicCommand)


    def test(self):
        self.sendCommand("test")
        time.sleep(0.1)
        self.sendCommand("shut_down")
        time.sleep(0.1)


if __name__ == "__main__":
    eng = Engine2("settings.conf")
    eng.test()



