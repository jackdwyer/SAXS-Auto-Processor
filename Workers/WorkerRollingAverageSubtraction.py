"""
Jack Dwyer

"""

from threading import Thread
import zmq
import sys
import time

from Core.Logger import log
from Core import DatFile
from Core import DatFileWriter

from Worker import Worker

class WorkerRollingAverageSubtraction(Worker):
    def __init__(self):
        Worker.__init__(self, "WorkerRollingAverageSubtraction")
        
        self.subtractedDatIntensities = []
        self.subtractedDatq = []
        self.subtractedErrors = []
        
        #For adding to be cleared when new user/sample
        self.addToClearList(self.subtractedDatIntensities)
        self.addToClearList(self.subtractedDatq)
        self.addToClearList(self.subtractedErrors)

    def process(self, filter):
        if (filter == "average_buffer"):
            self.aveBuffer = self.pull.recv_pyobj()
            log(self.name, "Buffer received")
            print self.aveBuffer
            
        if (filter == "clear_buffer"):
            log(self.name, "TOLD TO CLEAR TEH BUFFER")
        
        if (filter == "test"):
            log(self.name, "RECIEVED - 'test' message")
        
        
        if (filter == "static_image"):
            self.datFile = self.pull.recv_pyobj()
            log(self.name, "Static Image Received")
            #self.average()
            #self.imageSubtraction()

                
    def average(self):
        self.allIntensities.append(self.datFile.intensities)
        self.allQ.append(self.datFile.q)
        self.allErrors.append(self.datFile.errors)

        #averaging out
        self.aveIntensities = self.ave.average(self.allIntensities)
        self.aveQ = self.ave.average(self.allQ)
        self.aveErrors = self.ave.average(self.allErrors)
        

        log(self.name, "Averaging Completed")
        
        self.subtract(self.aveBuffer)
        
        self.datWriter.writeFile("/home/ics/jack/beam/", self.name, { 'q': self.aveQ, 'i' : self.aveIntensities, 'errors':self.aveErrors})
        
        





    def imageSubtraction(self):
        subtractedDatIntensities = []
        subtractedDatq = []
        subtractedErrors = []
        for i in range(len(self.dateFile.intensities)):
            #Intensities
            value = self.datFile.intensities[i] - self.aveBuffer[i]
            subtractedDatIntensities.insert(i, value)
            #Q Values
            subtractedDatq.insert(i, self.datFile.q[i])
            subtractedErrors.insert(i, self.datFile.errors[i])
        
        
        self.subtractedDatIntensities = subtractedDatIntensities
        self.subtractedDatq = subtractedDatq
        self.subtractedErrors = subtractedErrors

        fileName = self.datFile.getFileName()
        
        self.datWriter.writeFile(self.absolutePath + "sub/raw_sub" , str(fileName) , { 'q' : self.subtractedDatq, 'i' : self.subtractedDatIntensities, 'errors' : self.subtractedErrors})
        log(self.name, "Static Image Written ->" + fileName)


        




if __name__ == "__main__":
    pushPort = 4000
    reqPort = 8000
    context = zmq.Context()
    replyPass = False

    print "TEST 1 - ONLY PUSH/PULL"
    #Test 1 - Only a pull socket
    b = WorkerRollingAverageSubtraction()
    t = Thread(target=b.connect, args=(pushPort, False))
    t.start()

    
    testPush = context.socket(zmq.PUSH)
    testPush.bind("tcp://127.0.0.1:"+str(pushPort))
    testPush.send("clear")
    time.sleep(0.1)
    testPush.close()


    #Test 2
    print "TEST 2 - ONLY REQ/RECV"
    b = WorkerRollingAverageSubtraction()
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
