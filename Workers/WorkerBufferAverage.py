"""
Jack Dwyer
24 April 2012
refactored WorkerBufferAverage
"""

import sys
import time
from threading import Thread
sys.path.append("../")
import zmq
from Core import AverageList
from Core.Logger import log
from Core import DatFile

from Worker import Worker
from threading import Thread


class WorkerBufferAverage(Worker):
    def __init__(self):
        Worker.__init__(self, "WorkerBufferAverage")
        self.allIntensities = []
        self.aveIntensities = []
        
        self.addToClearList(self.allIntensities)
    
<<<<<<< HEAD
        self.reply = self.context.socket(zmq.REP)
    
=======
        #self.sendDataThread = Thread(target=self.sendData())
>>>>>>> work
    
    def process(self, filter):
        if (filter == "test"):
            log(self.name, "RECIEVED - 'test' message")
            
        if (filter == "buffer"):
            self.datFile = buffers.recv_pyobj()
            self.average()
            
<<<<<<< HEAD
    
    def average(self):
        self.allIntensities.append(self.datFile.intensities)
        self.allQ.append(self.datFile.q)
        self.allErrors.append(self.datFile.errors)

        #averaging out
        self.aveIntensities = self.ave.average(self.allIntensities)
        self.aveQ = self.ave.average(self.allQ)
        self.aveErrors = self.ave.average(self.allErrors)
        
        self.datWriter.writeFile(self.absolutePath, self.name, { 'q': self.aveQ, 'i' : self.aveIntensities, 'errors':self.aveErrors})

        Logger.log(self.name, "Averaging Completed")
        
        
=======
        if (filter == "reqBuffer"):
            log(self.name, "Requested Buffer")
>>>>>>> work
            
    def connect(self, pullPort, replyPort):
        self.pull.connect("tcp://127.0.0.1:"+str(pullPort))
        self.reply.bind("tcp://127.0.0.1:"+str(replyPort))
        log(self.name, "All Ports Connected -> pullPort: "+str(pullPort)+" - replyPort: "+str(replyPort))
        
        self.run()

    
    
    def average(self):
        self.allIntensities.append(self.datFile.intensities)
        self.allQ.append(self.datFile.q)
        self.allErrors.append(self.datFile.errors)

        #averaging out
        self.aveIntensities = self.ave.average(self.allIntensities)
        self.aveQ = self.ave.average(self.allQ)
        self.aveErrors = self.ave.average(self.allErrors)
        
        self.datWriter.writeFile(self.absolutePath, self.name, { 'q': self.aveQ, 'i' : self.aveIntensities, 'errors':self.aveErrors})

        Logger.log(self.name, "Averaging Completed")
        
        
    #Overidden from the connect constructor in worker
    def connect(self, pullPort, replyPort):
        self.pull.connect("tcp://127.0.0.1:"+str(pullPort))
        
        log(self.name, "All Ports Connected -> pullPort: "+str(pullPort)+" - replyPort: "+str(replyPort))
        
        #self.sendDataThread.start()
        self.run()

    
    
    #Need to override the run method, as we only want the buffer to clear if there is a new buffer
    def run(self):
        replyThread = Thread(target=self.sendData)
        replyThread.start()
        try:
            while True:
                filter = self.pull.recv()
                if (filter == 'clear'): #Need to make it check if the next image is a buffer, or if its a request.
                    self.clear()
                if (filter == 'test'):
                    print "WORKING"
                else:
                    self.process(filter)
                
        except KeyboardInterrupt:
            pass
    
<<<<<<< HEAD
    def sendData(self):
        try:
            while True:
                req = self.reply.recv() #wait for request of buffer
                if (req == "buffer"):
                    self.reply.send_pyobj(self.aveBuffer)
                    
                #Test    
                if (req == "testReply"):
                    self.reply.send_pyobj(req)

=======
    
    
    
    def sendData(self):
        reply = self.context.socket(zmq.REP)
        reply.bind("tcp://127.0.0.1:5000")
        try:
            while True:
                filter = reply.recv() #wait for request of buffer
                if (filter == 'test'):
                    reply.send_pyobj("REQUESTED DATA")
                if (filter == "reqBuffer"):
                    log(self.name, "BufferRequested")
                
        
>>>>>>> work
        except KeyboardInterrupt:
            pass   

        



if __name__ == "__main__":
    pushPort = 4000
    reqPort = 8000
    context = zmq.Context()
    replyPass = False




    #Test 2
    print "TEST 2 - ONLY REQ/RECV"
    b = WorkerBufferAverage()
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
