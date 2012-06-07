"""
Jack Dwyer
03/April/2012

To simplify the engine

YAML Config for:
 - Database settings
 - Which workers to spool up, with dynamically created ports
 - WorkerPipelines (for after the creation of the subtracted average)

Engine2 will replace Engine1 very soon 
 
"""     
import yaml
import WorkerDB

import epics
import time
import zmq
from Core import DatFile
from Core import LogLine
from Core import Logger
from Core import DirectoryCreator
import MySQLdb as mysql


class Engine2():

    def __init__(self, configFile):
        self.name = "Engine"
        self.context = zmq.Context()
        
        #Get all configuration details to pass off to workers
        try:
            stream = file(configFile, 'r') 
        except IOError:
            Logger.log(self.name, "Unable to find configuration, exiting.")
            exit()
            
        self.config = yaml.load(stream)
        
        self.directoryCreator = DirectoryCreator.DirectoryCreator(self.config['location'])

        #Create all workers
        self.workers = {}
        self.generateWorkers(self.config['workers'])
    
        #Wait for experiment to start
        self.run()
        
        
    def generateWorkers(self, workers):
        #Force Load WorkerDB
        #dbWorker = WorkerDB.WorkerDB(host = self.config['database']['host'], user = self.config['database']['user'], password = self.config['database']['password'])

        #TODO: Relative Location of imports
        """Loads all workers and puts them into a dictionary"""
        port = 7880 #TCP port used
        for worker in workers:
            workerModule = __import__(worker)
            workerModule.__dict__.update({"port" : port})
            mod = getattr(workerModule, worker)
            x = mod()
            x.connect(port)
            
            wbind = self.context.socket(zmq.PUSH)
            bindLocation = wbind.bind("tcp://127.0.0.1:7881")  
            
          
            
            self.workers[worker] = {"worker" : x, "port" : port, "bind" : bindLocation}
            
            
            port = port + 1

        Logger.log(self.name, "All workers generated")
        
        
    def generateDB(self):
        """
        """
        a = 2


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
        



if __name__ == "__main__":
    engine = Engine2('config.yaml')
    engine.userChange("/mnt/images/data/Cycle_2012_1/Pelliccia_4562")

    