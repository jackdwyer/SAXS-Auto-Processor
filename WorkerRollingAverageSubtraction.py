#!/usr/bin/env python2.7
"""
Jack dywer
23 march 2012

Averages the Static Image, and subtracts the averaged Buffer Average
"""

import zmq
from CommonLib import Logger
from CommonLib import DatFile
from CommonLib import DatFileWriter

import sys
import time
from threading import Thread


class WorkerRollingAverageSubtraction():

    def __init__(self):
        self.name = "WorkerRollingAverageSubtraction" # For logging
        Logger.log(self.name, "Worker Generated")
        
        self.allIntensities = []
        self.allQ = []
        self.allErrors = []
        
        self.aveIntensities = []
        self.aveQ = []
        self.aveErrors = []
               
        self.subtractedIntensities = []
        
        self.ave = AverageList.AverageList()
        self.datWriter = DatFileWriter.DatFileWriter()


    
    def run(self, datFile, aveBuffer):
        self.allIntensities.append(datFile.intensities)
        self.allQ.append(datFile.q)
        self.allErrors.append(datFile.errors)

        #averaging out
        self.aveIntensities = self.ave.average(self.allIntensities)
        self.aveQ = self.ave.average(self.allQ)
        self.aveErrors = self.ave.average(self.allErrors)

        Logger.log(self.name, "Averaging Completed")
        
        self.subtract(aveBuffer)
        
        self.datWriter.writeFile("Sim/testWriter", "newTEST", { 'q': self.aveQ, 'i' : self.aveQ, 'erros':self.aveErrors})
        
        

        
               
        
    def subtract(self, buffer):
        subtractedIntensities = []
        for i in range(len(self.aveIntensities)):
            value = self.aveIntensities[i] - buffer[i]
            subtractedIntensities.insert(i, value)
        
        self.subtractedIntensities = subtractedIntensities
        
        Logger.log(self.name, "Subtraction Completed")
        
        
    def writeFile(self, name):
        location = "testRolling/" + str(name)
        f = open(location, 'w')
        f.write(name + "\n")
        f.write('%14s %16s %16s \n' % ('q', 'I', 'Err')) #Needed for string formatting
        for i in range(len(self.aveIntensities)):
            f.write('%18.10f %16.10f %16.10f \n' % (self.aveQ[i], self.aveIntensities[i], self.aveErrors[i]))        
        f.close()
        
        print "file written"
        
        
        
        
        
        
        
        
        
        
        

if __name__ == "__main__":
    worker = WorkerRollingAverageSubtraction()

    if len(sys.argv) > 1 and sys.argv[1] == "tests":
        b = [1,1,1]
        dat = DatFile.DatFile("t.dat")
        worker.run(dat, b)

    else:    

        context = zmq.Context()

        #TODO, possible sub/pub so only one socket for all samples
        samples = context.socket(zmq.PULL)
        samples.connect("tcp://127.0.0.1:7885")

        bufferReq = context.socket(zmq.REQ)
        bufferReq.connect("tcp://127.0.0.1:7883")


        firstTime = True
        aveBuffer = []

        while True:
            datFile = samples.recv_pyobj()
            print "recieved the datFile"
            if (firstTime):
                bufferReq.send("REQ-AVEBUFFER")
                aveBuffer = bufferReq.recv_pyobj()
                firstTime = False

            worker.run(datFile, aveBuffer)
     

