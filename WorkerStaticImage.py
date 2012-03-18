#!/usr/bin/env python2.7
"""
Jack dywer
18 march 2012
"""


import zmq
import DatFile
import sys

class WorkerStaticImage():
    
    def __init__(self):
        self.allIntensities = []
    
    
    def run(self, bufferFile):
        bufferObject = DatFile.DatFile(bufferFile)
        self.allIntensities.append(bufferObject.getIntensities())
            
    def getAveBuffer(self):
        return self.allIntensities


if __name__ == "__main__":
    worker = WorkerStaticImage()
    
    if len(sys.argv) > 1 and sys.argv[1] == "tests":
        worker.run("testDat/0p009_0166.dat")
        print worker.getAveBuffer()
    
    else:
        context = zmq.Context()

        samples = context.socket(zmq.PULL)
        samples.connect("tcp://127.0.0.1:7889")
        
        bufferReq = context.socket(zmq.REQ)
        bufferReq.connect("tcp://127.0.0.1:7880")
        

        
        while True:
            data = samples.recv()
            bufferReq.send("gimme")
            bufferBlah = bufferReq.recv()
        
            print bufferBlah
            print "^666666666666666666666666666666666666666666666666666"
            print "got SAMPLE %s" % data
            worker.run(data)
            print worker.getAveBuffer()
         

