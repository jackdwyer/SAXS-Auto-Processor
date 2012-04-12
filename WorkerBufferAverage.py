 #!/usr/bin/env python2.7
"""
Jack dywer
18 march 2012
"""

import zmq
from CommonLib import AverageList
from CommonLib import Logger
from CommonLib import DatFile

import sys
import time
from threading import Thread


class WorkerBufferAverage():
    
    def __init__(self):
        self.name = "WorkerBufferAverage" #For logging
        Logger.log(self.name, "Worker Generated")

        self.allIntensities = []
        self.aveIntensities = []
        self.ave = AverageList.AverageList()
        
        self.user = ""
        self.experiment = ""
    
    
    def run(self, datFile):
        self.allIntensities.append(datFile.intensities)
        self.aveIntensities = self.ave.average(self.allIntensities)
        Logger.log(self.name, "Average Buffer Generated")
  
    def getAve(self):
        return self.aveIntensities
    
    def clear(self):
        """Clear out function for when a new experiment is starting"""
        self.allIntensities = []
        self.aveIntensities = []
        Logger.log(self.name, "Worker Cleared - all buffers forgotten")
        
    def updateRecords(self, user, experiment):
        self.user = user
        self.experiment = experiment
    
    
    

def send_buffer_data(context, worker):
    bufferReply = context.socket(zmq.REP)
    bufferReply.bind("tcp://127.0.0.1:7883")
    
    try:
        while True:
            req = bufferReply.recv() #wait for request of buffer
            bufferReply.send_pyobj(worker.aveIntensities)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    worker = WorkerBufferAverage()
    
    if len(sys.argv) > 1 and sys.argv[1] == "tests":
        d = DatFile.DatFile("Sim/data/0p009_0166.dat")
        worker.run(d)
    
    else:
        context = zmq.Context()

        buffers = context.socket(zmq.PULL)
        buffers.connect("tcp://127.0.0.1:7881")
        
        junk = Thread(target=send_buffer_data, args=(context, worker))
        junk.start()
        try:
            while True:
                #filter out what to do
                filter = buffers.recv()
                if (str(filter) == "datFile"):
                    datFile = buffers.recv_pyobj()
                    worker.run(datFile)
                    
                if (str(filter) == 'user'):
                    user = buffers.recv()
                    experiment = buffers.recv()
                    worker.updateRecords(user, experiment)

                if (str(filter) == 'recalculate_buffer'):
                    worker.clear()
                
                if (str(filter) == 'clear'):
                    worker.clear() 
                    
                
                
                

                
        except KeyboardInterrupt:
            pass
