#!/usr/bin/env python2.7
"""
Jack dywer
18 march 2012

23 March
- Fixing what is written out
"""

from threading import Thread
import zmq
import sys
import time

from Core.Logger import log
from Core import DatFile
from Core import DatFileWriter

from Worker import Worker

class WorkerStaticImage(Worker):
    def __init__(self):
        Worker.__init__(self, "WorkerStaticImage")
        
        self.subtractedDatIntensities = []
        self.subtractedDatq = []
        self.subtractedErrors = []
        
        #For adding to be cleared when new user/sample
        self.addToClearList(self.subtractedDatIntensities)
        self.addToClearList(self.subtractedDatq)
        self.addToClearList(self.subtractedErrors)

    def process(self, filter):
        if (filter == "image"):
            self.datFile = self.pull.recv_pyobj()
            log(self.name, "Static Image Received")
            
            if (self.needBuffer):
                self.reqBuffer.send("bufferRequest")
                self.aveBuffer = self.reqBuffer.recv_pyobj()
                self.imageSubtraction(self.datFile, self.aveBuffer)
                self.needBuffer = False

            else:
                self.imageSubtraction(self.datFile, self.aveBuffer)


    def imageSubtraction(self, datFile, aveBuffer):
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

        fileName = datFile.getFileName()
        
        self.datWriter.writeFile(self.absolutePath + "sub/raw_sub" , str(fileName) , { 'q' : self.subtractedDatq, 'i' : self.subtractedDatIntensities, 'errors' : self.subtractedErrors})
        log(self.name, "Static Image Written ->" + fileName)


        




if __name__ == "__main__":
    pushPort = 4000
    reqPort = 8000
    context = zmq.Context()
    replyPass = False

    print "TEST 1 - ONLY PUSH/PULL"
    #Test 1 - Only a pull socket
    b = WorkerStaticImage()
    t = Thread(target=b.connect, args=(pushPort, False))
    t.start()

    
    testPush = context.socket(zmq.PUSH)
    testPush.bind("tcp://127.0.0.1:"+str(pushPort))
    testPush.send("clear")
    time.sleep(0.1)
    testPush.close()


    #Test 2
    print "TEST 2 - ONLY REQ/RECV"
    b = Worker("Worker (Sub)")
    t = Thread(target=b.connect, args=(pushPort, reqPort))
    t.start()
    
    testReq = context.socket(zmq.REQ)
    testReq.connect("tcp://127.0.0.1:"+str(reqPort))
    testReq.send("testReply")
    testReply = testReq.recv_pyobj()
    
    if (testReply == "testReply"):
        replyPass = True

    testReq.close()
    
    if (replyPass):
        print "TEST OVER - Succeeded"
    else:
        print "TEST OVER - Failed with reply"


         

