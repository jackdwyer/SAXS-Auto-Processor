import logging
import sys
import zmq
import time
from threading import Thread
from Worker import Worker
from Core import AverageList
from Core import DatFile
from Core import DatFileWriter



class WorkerBufferAverage(Worker):    
    def __init__(self):
        Worker.__init__(self, "Worker Buffer Average")
        
        #Specific Class Variables
        self.averagedBuffer = None
        self.bufferIndex = 1
        self.buffers = []
        
        
        
    def processRequest(self, command, obj):                
        self.logger.info("Processing Received object")
        command = str(obj['command'])
        
        if (command == "buffer"):
            buffer = obj['buffer']
            self.logger.info("Buffer Sample")
            self.averageBuffer(buffer)
            
    def averageBuffer(self, buffer):
        self.buffers.append(buffer)
        intensities = []
        for buffer in self.buffers:
            intensities.append(buffer.intensities)
            
        datName = "avg_buffer_" + str(self.bufferIndex) + "_" +buffer.getBaseFileName()
        averageIntensities = self.averageList.average(intensities)
        self.datWriter.writeFile(self.absoluteLocation + "/avg/", datName, { 'q' : self.buffers[-1].getq(), "i" : averageIntensities, 'errors':self.buffers[-1].getErrors()})

        

    def rootNameChange(self):
        self.logger.info("Root Name Change Called - No Action Required")

    def newBuffer(self):
        self.averagedBuffer = None
        self.bufferIndex = self.bufferIndex + 1
    
    def clear(self):
        Worker.clear(self)
        self.averagedBuffer = None
        self.bufferIndex = 1
        self.buffers = []

        

if __name__ == "__main__":
    #Test Cases
    context = zmq.Context()
    port = 1200
    
    worker = WorkerBufferAverage()

    t = Thread(target=worker.connect, args=(port,))
    t.start()
    time.sleep(0.1)

    
    testPush = context.socket(zmq.PUSH)
    testPush.connect("tcp://127.0.0.1:"+str(port))
    testPush.send_pyobj({'command' : "averaged_buffer"})
    testPush.send_pyobj({'command' : "test"})
    testPush.send_pyobj({'command' : "test"})
    testPush.send_pyobj({'command' : "static_image"})
    testPush.send_pyobj({'command' : "test"})
    testPush.send_pyobj({'command' : "test"})
    testPush.send_pyobj({'command' : "averaged_buffer"})
    testPush.send_pyobj({'command' : "test"})
    testPush.send_pyobj({'command' : "test"})
    testPush.send_pyobj({'command' : "static_image"})
    testPush.send_pyobj({'command' : "test"})
    testPush.send_pyobj({'command' : "averaged_buffer"})
    testPush.send_pyobj({'command' : "shut_down"})