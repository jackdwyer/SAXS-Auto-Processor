import logging
import sys
sys.path.append("../")

import zmq
import time
from threading import Thread
from Worker import Worker
from Core import DatFile



class WorkerStaticImage(Worker):    
    def __init__(self):
        Worker.__init__(self, "Worker Static Image")
        
        #Specific Class Variables
        self.averagedBuffer = None
        
        
    def processRequest(self, command, obj):                
        command = str(obj['command'])
        
        if (command == "static_image"):
            self.logger.info("Received a static image")
            self.subtractBuffer(obj["static_image"], self.averagedBuffer)
        
        if (command == "averaged_buffer"):
            self.logger.info("Received an averaged buffer")
            try:
                self.setBuffer(obj['averaged_buffer'])
            except KeyError:
                self.logger.critical("Key Error at averaged_buffer")           

            
    
    def setBuffer(self, buffer):
        self.averagedBuffer = buffer
        self.logger.info("Set Averaged Buffer")
        print "DA BUFFER"
        print self.averagedBuffer
        
    def subtractBuffer(self, datFile, buffer):
        """Method for subtracting buffer from static sample """
        if (buffer):
            newIntensities = []
            print datFile.getIntensities()
            for i in len(datFile.getIntensities()):
                newIntensities.append(datFile.getIntensities()[i] - buffer[i])

            self.logger.info("Subtracting Buffer")
            print datFile
            print buffer
            print "######"
            print newIntensities
            
            datName = "sub_"+datFile.getBaseFileName()
            self.datWriter.writeFile(self.absoluteLocation + "/sub/", datName, { 'q' : datFile.getq(), "i" : newIntensities, 'errors':datFile.getErrors()})
            
            
            
            
            
        else:
            self.logger.critical("Error with Averaged Buffer, unable to perform subtraction")    
    
    def rootNameChange(self):
        self.logger.info("Root Name Change Called - No Action Required")
        
    def newBuffer(self):
        self.averagedBuffer = None
    
    
    def clear(self):
        Worker.clear(self)
        self.averagedBuffer = None
               

if __name__ == "__main__":
    #Test Cases
    context = zmq.Context()
    port = 1200
    
    worker = WorkerStaticImage()
    
    dat = DatFile.DatFile("sum_data_4.dat")

    t = Thread(target=worker.connect, args=(port,))
    t.start()
    time.sleep(0.1)

    
    testPush = context.socket(zmq.PUSH)
    testPush.connect("tcp://127.0.0.1:"+str(port))
    testPush.send_pyobj({'command' : "cleddar"})
    testPush.send_pyobj({'command' : "cleddar"})
    testPush.send_pyobj({'command' : "cleddar"})
    testPush.send_pyobj({'command' : "cleddar"})
    testPush.send_pyobj({'command' : "cleddar"})
    testPush.send_pyobj({'command' : "cleddar"})
    testPush.send_pyobj({'command' : "cleddar"})
    testPush.send_pyobj({'command' : "cleddar"})
    testPush.send_pyobj({'command' : "cleddar"})
    testPush.send_pyobj({'command' : "cleddar"})
    testPush.send_pyobj({'command' : "cleddar"})

    testPush.send_pyobj({'command' : "test"})
    testPush.send_pyobj({'command' : "test"})
    testPush.send_pyobj({'command' : "static_image"})
    testPush.send_pyobj({'command' : "test"})
    testPush.send_pyobj({'command' : "test"})
    testPush.send_pyobj({'command' : "averaged_buffer", "averaged_buffer":dat})
    testPush.send_pyobj({'command' : "test"})
    testPush.send_pyobj({'command' : "test"})
    testPush.send_pyobj({'command' : "static_image"})
    testPush.send_pyobj({'command' : "test"})
    testPush.send_pyobj({'command' : "averaged_buffer"})
    testPush.send_pyobj({'command' : "shut_down"})