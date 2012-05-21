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
        
        self.allIntensities = []
        self.allQ = []
        self.allErrors = []
        
        
        #For adding to be cleared when new user/sample
        self.addToClearList(self.subtractedDatIntensities)
        self.addToClearList(self.subtractedDatq)
        self.addToClearList(self.subtractedErrors)

    def process(self, test):       
        if (str(test) == "test"):
            log(self.name, "RECIEVED - 'test' message")
        
        
        if (str(test) == "static_image"):
            self.datFile = self.pull.recv_pyobj()
            log(self.name, "Static Image Received")
            self.average()
            self.imageSubtraction()

                
    def average(self):
        self.allIntensities.append(self.datFile.intensities)
        self.allQ.append(self.datFile.q)
        self.allErrors.append(self.datFile.errors)

        #averaging out
        self.aveIntensities = self.ave.average(self.allIntensities)
        self.aveQ = self.ave.average(self.allQ)
        self.aveErrors = self.ave.average(self.allErrors)
        

        log(self.name, "Averaging Completed")
        
        fileName = "sample_"+self.datFile.getBaseFileName()
        
        if (self.newSample):      
            self.dbPush.send("average_image")
            self.dbPush.send(fileName)
            self.newSample = False
        
        
        self.datWriter.writeFile(self.absoluteLocation+"/avg/", fileName, { 'q': self.aveQ, 'i' : self.aveIntensities, 'errors':self.aveErrors})
        
        
    def imageSubtraction(self):
        subtractedDatIntensities = []
        subtractedDatq = []
        subtractedErrors = []
        for i in range(len(self.datFile.intensities)):
            #Intensities
            value = self.datFile.intensities[i] - self.aveBuffer["intensities"][i]
            subtractedDatIntensities.insert(i, value)
            #Q Values
            subtractedDatq.insert(i, self.datFile.q[i])
            subtractedErrors.insert(i, self.datFile.errors[i])
        
        
        self.subtractedDatIntensities = subtractedDatIntensities
        self.subtractedDatq = subtractedDatq
        self.subtractedErrors = subtractedErrors

        fileName = "average_"+self.datFile.getBaseFileName()
        
        if (self.newSample_sub):
            self.dbPush.send("subtracted_average_image")
            self.dbPush.send(fileName)
            self.newSample_sub = False
        
        self.datWriter.writeFile(self.absoluteLocation + "/sub/" , fileName , { 'q' : self.subtractedDatq, 'i' : self.subtractedDatIntensities, 'errors' : self.subtractedErrors})
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
