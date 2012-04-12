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
from Workers import WorkerDB, WorkerBufferAverage, WorkerStaticImage


class Engine2():

    def __init__(self, configFile):
        #Get all configuration details to pass off to workers
        stream = file(configFile, 'r') 
        self.config = yaml.load(stream)
    
        self.workers = {}
        self.loadWorkers(self.config['workers'])
    
        print self.workers
        
    def loadWorkers(self, workers):
        #Force Load WorkerDB
        dbWorker = WorkerDB.WorkerDB(host = self.config['database']['host'], user = self.config['database']['user'], password = self.config['database']['password'])

        for worker in workers:
            workerModule = __import__(worker, level=2, globals=globals())
            mod = getattr(workerModule, worker)
            x = mod()
            self.workers[worker] = x
    


if __name__ == "__main__":
    engine = Engine2('config.yaml')