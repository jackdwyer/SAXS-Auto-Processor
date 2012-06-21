import os

class DatFile:
    """
    .. codeauthor:: Jack Dwyer <jackjack.dwyer@gmail.com>
    Takes a path to a datFile, parses it and calculates the respective High/Low Q's
     
    Args:
        datFilePath (String): Absolute location of the datFile as told from the local machine
    """
    def __init__(self, datFilePath):
        self.datFilePath = datFilePath
        self.q = []
        self.intensities = []
        self.errors = []

        self.numLines = 0 
        self.IQL = 0.0
        self.IHQ = 0.0
        self.valid = False
        self.nonAir = False
        self.processDatFile()
        self.processHighLowQ()


    def openDatFile(self):
        f = open(self.datFilePath, "r")
        return f    
    
    def closeDatFile(self, f):
        try:
            f.close()
            return True
        except ValueError:
            raise Exception("Dat File did not close")

    def getFileName(self):
        """
        | Returns the file name of the datFile
        | eg: datFile1.dat
        """
        return os.path.basename(self.datFilePath)
    
    def getBaseFileName(self):
        """
        | Returns the base name of the sample type
        | eg: SampleType1_1555.dat becomes SampleType1.dat
        """
        fileName = self.getFileName()
        h = fileName.split("_")
        del h[-1]
        g = ""
        for i in h:
            g = g + i + "_"
        return g + ".dat"

    def getDatFilePath(self):
        return self.datFilePath
    
    def isValid(self):
        return self.valid
        

    def getq(self):
        """
        Returns q values
        """
        return self.q
    
    def getIntensities(self):
        """
        Returns Intensities
        """
        return self.intensities
    
    def getErrors(self):
        """
        Returns Errors
        """
        return self.errors
 
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
        
    def processHighLowQ(self):
        self.findILQ()
        self.findIHQ()
        
    def findILQ(self, start = 3 , end = 20):
        self.ILQ  = sum(self.intensities[start:end])
        #self.ILQ = float(sum(self.ILQ)) / len(self.ILQ)
    
    def findIHQ(self, start = -20, end = -1): 
        self.IHQ = sum(self.intensities[start:end])
        
        
    def processDatFile(self):
        """
        | Process the 3 column datfile placing each column data into its correct type
        | Based off some code by Nathan Cowieson
        """

        f  = self.openDatFile()
        line = f.readline()
        numLines = 0
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
        
    def getValues(self):
        """
        Returns a dictionary of all the values
        """
        return { 'q' : self.q, 'intensities' : self.intensities, 'errros' : self.errors }
        
    def reprocessDatFile(self):
        self.processDatFile()
        
    def getIHQ(self):
        """
        Returns High Q
        """
        return self.IHQ 
    
    def getILQ(self):
        """
        Returns Low Q
        """        
        return self.ILQ
    

if __name__ == "__main__":
    b = DatFile("../data/dat/air_1_0001.dat")
    print b.getFileName()

    
