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
from workers import WorkerDB


class Engine2():

    def __init__(self, configFile):
        #Get all configuration details to pass off to workers
        stream = file(configFile, 'r') 
        self.config = yaml.load(stream)
        
        
        print self.config['database']['host']
        
        
        #Will always have Definate workers for the averaged Subtraction to occur
        self.workers  = {'bufferAverage' : 'WorkerBufferAverage', 'dbWriter' : 'WorkerDB' }
        
        self.loadWorkers()
        
        
    
    def loadWorkers(self):
        #Will begin with the DB worker
        dbWorker = WorkerDB.WorkerDB(host = self.config['database']['host'], user = self.config['database']['user'], password = self.config['database']['password'])


if __name__ == "__main__":
    engine = Engine2('config.yaml')