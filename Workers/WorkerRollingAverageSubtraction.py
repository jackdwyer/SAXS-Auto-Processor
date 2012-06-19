"""
Jack Dwyer
"""

import logging
import sys
import zmq
import time
from threading import Thread
from Worker import Worker
from Core import AverageList
from Core import DatFile
from Core import DatFileWriter



class WorkerRollingAverageSubtraction(Worker):    
    def __init__(self):
        Worker.__init__(self, "Worker Rolling Average Subtraction")
        
        #Class specific variables
        self.averagedBuffer = None
        self.datFiles = []
        self.datIndex = 1
        
    def processRequest(self, command, obj):
        command = str(obj['command'])
        
        if (command == "static_image"):
            self.logger.info("Received a static image")
            self.subAvIntensities(obj['static_image'])
            #Then Subtract
        
        if (command == "averaged_buffer"):
            self.logger.info("Received an averaged buffer")
            try:
                self.setBuffer(obj['averaged_buffer'])
            except KeyError:
                self.logger.critical("Key Error at averaged_buffer")
                
    
    
    
    def subAvIntensities(self, datFile):
        self.datFiles.append(datFile)
        intensities = []
        for datFile in self.datFiles:
            intensities.append(datFile.getIntensities())
        
        averagedIntensities = self.averageList.average(intensities)



        datName = "avg_sample_" + str(self.datIndex) + "_" +datFile.getBaseFileName()
        if (averagedIntensities):
            self.datWriter.writeFile(self.absoluteLocation + "/avg/", datName, { 'q' : datFile.getq(), "i" : averagedIntensities, 'errors':datFile.getErrors()})
            self.pub.send_pyobj({"command":"averaged_sample", "location":datName})


        
        datName = "avg_sub_sample_" + str(self.datIndex) + "_" +datFile.getBaseFileName()
        
        subtractedIntensities = self.subtractBuffer(averagedIntensities, self.averagedBuffer)
        
        if (subtractedIntensities):
            self.datWriter.writeFile(self.absoluteLocation + "/sub/", datName, { 'q' : datFile.getq(), "i" : subtractedIntensities, 'errors':datFile.getErrors()})
            self.pub.send_pyobj({"command":"averaged_subtracted_sample", "location":datName})


        

    def subtractBuffer(self, intensities, buffer):
        if (buffer):
            newIntensities = []
            for i in range(0, len(intensities)):
                newIntensities.append(intensities[i] - buffer[i])
            return newIntensities
        else:
            self.logger.critical("Error with Averaged Buffer, unable to perform subtraction")    
    
    
    
    def setBuffer(self, buffer):
        self.averagedBuffer = buffer
        self.logger.info("Set Averaged Buffer")
        
    def rootNameChange(self):
        self.datFiles = []
        self.datIndex = self.datIndex + 1
    
    def newBuffer(self):
        self.datFiles = []
        self.averagedBuffer = None
        
    def clear(self):
        Worker.clear(self)
        self.averagedBuffer = None
        self.datIndex = 1