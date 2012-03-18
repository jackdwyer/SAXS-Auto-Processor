#!/usr/bin/env python2.7
"""
Jack dywer
18 march 2012
"""

import zmq
import DatFile
import sys
import time
from threading import Thread

class WorkerBufferAverage():
    
    def __init__(self):
        self.allIntensities = []
    
    
    def run(self, bufferFile):
        bufferObject = DatFile.DatFile(bufferFile)
        self.allIntensities.append(bufferObject.getIntensities())


            
    def getAveBuffer(self):
        return self.allIntensities

def send_buffer_data(context, worker):
    bufferReply = context.socket(zmq.REP)
    bufferReply.bind("tcp://*:7880")
    
    while True:
        req = bufferReply.recv() #wait for request of buffer
        test = "testdata"
        bufferReply.send(test)

if __name__ == "__main__":
    worker = WorkerBufferAverage()
    
    if len(sys.argv) > 1 and sys.argv[1] == "tests":
        worker.run("testDat/0p009_0166.dat")
        print worker.getAveBuffer()
    
    else:
        context = zmq.Context()

        buffers = context.socket(zmq.PULL)
        buffers.connect("tcp://127.0.0.1:7888")
        
        junk = Thread(target=send_buffer_data, args=(context, worker))
        junk.start()
        
        while True:
            data = buffers.recv()
            print "got data %s" % data
            worker.run(data)
            print worker.getAveBuffer()
            