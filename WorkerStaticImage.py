#!/usr/bin/env python2.7
"""
Jack dywer
18 march 2012

23 March
- Fixing what is written out
"""


import zmq
from CommonLib import TableBuilder
import sys

class WorkerStaticImage():
    
    def __init__(self):
        self.subtractedDatIntensities = []
        self.subtractedDatq = []
        self.subtractedErrors = []
        
        #For writting to DB
        self.context = zmq.Context()
        self.dbWorker = self.context.socket(zmq.PUSH)
        self.dbWorker.connect("tcp://127.0.0.1:7884")
  
       
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
        self.subtractedDatq = subtractedErrors
        name = datFile.getFileName()
        self.writeFile(name)
        


    def writeFile(self, name):
        location = "testWrite/" + "subtracted-" + str(name)
        f = open(location, 'w')
        f.write('%14s %16s %16s' % ('q', 'I', 'Err')) #Needed for string formatting
        for i in range(len(self.subtractedDatq)):
            f.write("[" + str(self.subtractedDatq[i]) + ", " + str(self.subtractedDatIntensities[i]) + "] , \n")
        
        f.close()
        self.exportData(location)
        
        print "file written"
        

    def exportData(self, location):
        self.dbWorker.send("ImageLocation")
        self.dbWorker.send(str(location))

        
        
        
        
        
        

if __name__ == "__main__":
    worker = WorkerStaticImage()
    
    if len(sys.argv) > 1 and sys.argv[1] == "tests":
        worker.writeFile("TestWrite")
        
        
    
    else:
        context = zmq.Context()

        samples = context.socket(zmq.PULL)
        samples.connect("tcp://127.0.0.1:7882")
        
        bufferReq = context.socket(zmq.REQ)
        bufferReq.connect("tcp://127.0.0.1:7883")
        

        

        
        while True:
            datFile = samples.recv_pyobj()
            bufferReq.send("REQ-AVEBUFFER")
            aveBuffer = bufferReq.recv_pyobj()
            worker.run(datFile, aveBuffer)
         

