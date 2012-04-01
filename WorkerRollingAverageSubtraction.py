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
        print "worker generated"
        self.allIntensities = []
        self.allQ = []
        self.allErrors = []
        
        self.aveIntensities = []
        self.aveQ = []
        self.aveErrors = []
               
        self.subtractedIntensities = []

    
    def run(self, datFile, aveBuffer):
        self.allIntensities.append(datFile.intensities)
        self.allQ.append(datFile.q)
        self.allErrors.append(datFile.errors)

        if (len(self.allIntensities) > 1):
            self.generateIntensityAverage()
            self.generateQAverage()
            self.generateErrorAverage()
            self.writeFile("rolling_average1.dat")
        else:
            print "only 1 dat file.. unable to average"
        
        
    def generateIntensityAverage(self):
        value = 0.0
        aveIntensities = []
        #knows now the length of each list
        print len(self.allIntensities)
        for i in range(len(self.allIntensities[0])):
            #so now it should index against each list
            for x in range(len(self.allIntensities)):
                b = self.allIntensities[x][i]
                value = value + b
            aveIntensities.insert(x, value)
            
        self.aveIntensities = aveIntensities
        
        
        print self.aveIntensities
        
    def generateQAverage(self):
        value = 0.0
        #Loop across list and create averages
        aveQ = []
        for i in range(len(self.allQ[0])):
            for x in range(len(self.allQ)):
                value = self.allQ[x][i] + value
            value = (value/(len(self.allQ)))    
            aveQ.insert(x, value)
            
        self.aveQ = aveQ
            
    def generateErrorAverage(self):
        value = 0.0
        #Loop across list and create averages
        aveErrors = []
        for i in range(len(self.allErrors[0])):
            for x in range(len(self.allErrors)):
                value = self.allErrors[x][i] + value
            value = (value/(len(self.allErrors)))    
            aveErrors.insert(x, value)
        self.aveErrors = aveErrors
        
        
    def subtract(self, buffer):
        subtractedIntensities = []
        for i in range(len(self.aveIntensities)):
            value = self.aveIntensities[i] - buffer[i]
            subtractedIntensities.insert(i, value)
        
        self.subtractedIntensities = subtractedIntensities
        
        
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
     

