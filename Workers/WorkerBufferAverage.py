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
from Core.Logger import logger
from Core import DatFile

from Worker import Worker


class WorkerBufferAverage(Worker):
    def __init__(self):
        Worker.__init__(self, "WorkerBufferAverage")
        self.allIntensities = []
        self.allErrors = []
        self.allQ = []
        
        self.avIntensities = []
        self.avErrors = []
        self.avQ = []
        
        #self.addToClearList(self.allIntensities, self.allErrors, self.allQ)
        self.reply = self.context.socket(zmq.REP)

        #self.sendDataThread = Thread(target=self.sendData())
        
        self.index = 0
        
        self.changeInBuffer = True

    
    def process(self, test):       
        if (test == "test"):
            logger(self.name, "RECIEVED - 'test' message")
            
            
            
        if (test == "buffer"):
            buffer = self.pull.recv_pyobj()
            logger(self.name, "RECIEVED - Buffer")
            self.average(buffer)
            
    def newBuffer(self):
        self.changeInBuffer = True
        self.index = self.index + 1
        self.allIntensities = []
        self.allErrors = []
        self.allQ = []
        self.avIntensities = []
        self.avErrors = []
        self.avQ = []
        
    def clear(self):
        self.index = 0
        self.allIntensities = []
        self.allErrors = []
        self.allQ = []
        self.avIntensities = []
        self.avErrors = []
        self.avQ = []
            
    
    def average(self, datBuffer):
        self.allIntensities.append(datBuffer.intensities)
        self.allErrors.append(datBuffer.errors)
        self.allQ.append(datBuffer.q)


        #averaging out
        self.avIntensities = self.ave.average(self.allIntensities)
        self.avErrors = self.ave.average(self.allErrors)
        self.avQ = self.ave.average(self.allQ)
        
        fileName = "buffer" + str(self.index) + "_avg_" + str(datBuffer.getBaseFileName())

        if (self.changeInBuffer):
            self.dbPush.send("buffer_file")
            self.dbPush.send(fileName)
            self.changeInBuffer = False
        
        self.datWriter.writeFile(self.absoluteLocation+"/avg/", fileName, { 'q': self.avQ, 'i' : self.avIntensities, 'errors':self.avErrors})

        logger(self.name, "Averaging Completed")


            
    def connect(self, pullPort, dbPushPort, replyPort):
        
        self.pull.connect("tcp://127.0.0.1:"+str(pullPort));
        self.reply.bind("tcp://127.0.0.1:"+str(replyPort))

        
        if (dbPushPort):
            self.dbPush.connect("tcp://127.0.0.1:"+str(dbPushPort))
            logger(self.name, "All Ports Connected -> pullPort: "+str(pullPort) + "-> replyPort: "+str(replyPort)+" -> dbPushPort: "+str(dbPushPort))
        
        else:
            logger(self.name, "All Ports Connected -> pullPort: "+str(pullPort) + "-> replyPort: "+str(replyPort))
        
            


        logger(self.name, "All Ports Connected -> replyPort: "+str(replyPort))
        
        replyThread = Thread(target=self.sendData)
        replyThread.setDaemon(True)
        replyThread.start()

        self.run()


    def getAverageBuffer(self):
        return {'intensities' : self.avIntensities, 'errors' : self.avErrors, 'q' : self.avQ}
    
    
    def sendData(self):
        try:
            while True:
                test = self.reply.recv() #wait for request of buffer
                if (test == 'test'):
                    self.reply.send_pyobj("REQUESTED DATA")
                if (test == "request_buffer"):
                    logger(self.name, "BufferRequested")
                    v = self.getAverageBuffer()
                if (v['intensities']):
                    self.reply.send_pyobj(self.getAverageBuffer())
                else:
                    self.reply.send_pyobj("no_buffer")
                    

        

        except KeyboardInterrupt:
            pass   
        
        #OVERRIDE IN BUFFER
    def close(self):
        """Close all zmq sockets"""
        self.pull.close()
        self.reply.close()
        logger(self.name, "Sockets Closed")
        sys.exit()
        



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
