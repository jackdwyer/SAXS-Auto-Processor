#!/usr/bin/env python2.7
"""
Jack dywer
18 march 2012

23 March
- Fixing what is written out
"""


import zmq
from CommonLib import Logger
from CommonLib import DatFile
from CommonLib import DatFileWriter
import sys

class WorkerStaticImage():
    
    def __init__(self):
        self.name = "WorkerStaticImage"  #for logging
        Logger.log(self.name, "Worker Generated")
        
        
        self.subtractedDatIntensities = []
        self.subtractedDatq = []
        self.subtractedErrors = []
        
        #For writting to DB
        self.context = zmq.Context()
        self.dbWorker = self.context.socket(zmq.PUSH)
        self.dbWorker.connect("tcp://127.0.0.1:7884")
        
        #for generic writting
        self.datWriter = DatFileWriter.DatFileWriter()
        
        self.firstTime = True
        
    def clear(self):
        self.subtractedDatIntensities = []
        self.subtractedDatq = []
        self.subtractedErrors = []
        self.firstTime = True
        Logger.log(self.name, "Worker Cleared - forgotten buffer")


       
    def run(self, datFile, aveBuffer):
        subtractedDatIntensities = []
        subtractedDatq = []
        subtractedErrors = []
        for i in range(len(datFile.intensities)):
            #Intensities
            value = datFile.intensities[i] - aveBuffer[i]
            subtractedDatIntensities.insert(i, value)
            #Q Values
            subtractedDatq.insert(i, datFile.q[i])
            subtractedErrors.insert(i, datFile.errors[i])
        
        
        self.subtractedDatIntensities = subtractedDatIntensities
        self.subtractedDatq = subtractedDatq
        self.subtractedErrors = subtractedErrors
        
        self.datWriter.writeFile("testWrite/", "staticImageTEst", { 'q' : self.subtractedDatq, 'i' : self.subtractedDatIntensities, 'errors' : self.subtractedErrors})
        

    def exportData(self, location):
        self.dbWorker.send("ImageLocation")
        self.dbWorker.send(str(location))


if __name__ == "__main__":
    worker = WorkerStaticImage()
    
    if len(sys.argv) > 1 and sys.argv[1] == "tests":
        buf = [1,1,1]
        dat = DatFile.DatFile("Sim/data/test.dat")
        worker.run(dat, buf)      
            
    else:
        context = zmq.Context()

        samples = context.socket(zmq.PULL)
        samples.connect("tcp://127.0.0.1:7882")
        
        bufferReq = context.socket(zmq.REQ)
        bufferReq.connect("tcp://127.0.0.1:7883")
        
        aveBufer = []

        while True:
            
            filter = samples.recv()
            if (str(filter) == "sample"):
                datFile = samples.recv_pyobj()
                Logger.log(worker.name, "Recieved DatFile")
                if (work.firstTime):
                    bufferReq.send("REQ-AVEBUFFER")
                    aveBuffer = bufferReq.recv_pyobj()
                    worker.firstTime = False
                worker.run(datFile, aveBuffer)
                
            if (str(filter) == 'clear'):
                worker.clear()
         

