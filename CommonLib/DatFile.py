""" 
Jack Dwyer
21/02/2012

Holds general methods on for the Dat Files to be processed
will also auto process datfile data into the q, i, error lists

18 March 2012 - Adding to the new zmq shit
"""

import os

class DatFile:
    
    def __init__(self, datFilePath):
        """Must pass the absolute dat file path """
        self.datFilePath = datFilePath
        self.q = []
        self.intensities = []
        self.errors = []
        self.processDatFile()
        self.numLines
        self.IQL = 0.0
        self.IHQ = 0.0
        self.valid = False
        self.nonAir = False
        
    
    def openDatFile(self):
        f = open(self.datFilePath)
        return f    
    
    def closeDatFile(self, f):
        try:
            f.close()
            return True
        except ValueError:
            raise Exception("Dat File did not close")

    def getFileName(self):
        return os.path.basename(self.datFilePath)

    def getDatFilePath(self):
        return self.datFilePath

    def getq(self):
        return self.q
    
    def getIntensities(self):
        return self.intensities
    
    def getErrors(self):
        return self.errors

    """ all set operators expect to be passed a list 
    TODO: check type, raise exception if not list 
    pretty not needed functions anyways"""   
    def setq(self, q):
        self.q = q
        
    def setIntensities(self, intensities):
        self.intensities = intensities
        
    def setErrors(self, errors):
        self.errors = errors
    
    def setNumLines(self, numLines):
        self.numLines = numLines
        
    def setValid(self, valid = False):
        self.valid = valid
        
    def findILQ(self, start = 3 , end = 20):
        self.ILQ = self.intensities[start:end]
        self.ILQ  = sum(self.intensities[start:end])
        #self.ILQ = float(sum(self.ILQ)) / len(self.ILQ)
        return self.ILQ
    
    def findIHQ(self, start = -20, end = -1): 
        self.IHQ = self.intensities[start:end]
        self.IHQ = sum(self.IHQ)
        return self.IHQ
        
        
    def processDatFile(self):
        """ Based of a read function written by Nathan Cowieson 
            Reads each line of .dat file, and enters each data value into its correct list"""
        f  = self.openDatFile()
        line = f.readline()
        numLines = 10
        while line:
            b =  line.split()
            try:
                q = float(b[0])
                i = float(b[1])
                e = float(b[2])
                self.q.append(q)
                self.intensities.append(i)
                self.errors.append(e)
            except IndexError:
                pass
            except ValueError:
                pass
            
            line = f.readline()
            numLines = numLines + 1

            
        self.closeDatFile(f)
        self.setNumLines(numLines)
        
    def reprocessDatFile(self):
        self.processDatFile()

    
        

    