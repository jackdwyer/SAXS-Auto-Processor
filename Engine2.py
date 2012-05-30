"""
Engine using standard configparse over pyYaml

Jack Dwyer

TODO import logging and use that across all workers/core/engine etc
"""
import logging
import sys

import zmq
import yaml

import imp

from Workers import Worker



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

        fp, pathname, description = imp.find_module("Workers/Worker")
        print fp, pathname, description

        #ZMQ Class Variables
        self.zmqContext = zmq.Context()

    
        #Instantiate all workers, get them all ready to push out into their own thread and connected up
        self.instantiateWorkers(self.workers)
    
    
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
            mod = __import__("Workers." + worker, level=1)
            v = getattr(mod, worker)
            x = v()
            instanceDict[worker] = x
    
        


if __name__ == "__main__":
    eng = Engine2("settings.conf")



