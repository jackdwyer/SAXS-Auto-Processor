"""
Jack Dwyer
31 March 2012

Common DatFileWriter averaging class/methods.  

expects a dictionary with q, i, error values
prints to an accuracy of 10 decimal places.

"""
import os
import Logger


class DatFileWriter:
    
    def __init__(self, accuracy = 10):
        self.name = "DatFileWriter"
        self.location = ""
        self.datName = ""
        self.data = {}
        self.accuracy = accuracy
   
        
    def writeFile(self, location, datName, dict):
        self.location = location
        self.datName = datName
        self.data = dict
        
        #Used for checking if the folder exists.. will be used later in engine
        if not os.path.exists(self.location):
            os.makedirs(self.location)
                   
        loc = self.location+self.datName                
        f = open(loc, 'w')
        f.write(self.datName + "\n")
        formatting  = '%'+str(4 + self.accuracy)+'s %'+str(6 + self.accuracy)+'s %'+str(6 + self.accuracy)+'s \n'
        f.write(formatting % ('q', 'I', 'Err')) #Needed for string formatting
        for i in range(len(self.data['q'])):
            formatting = '%'+str(8 + self.accuracy)+'.'+str(self.accuracy)+'f %'+str(6 + self.accuracy)+'.'+str(self.accuracy)+'f %'+str(6 + self.accuracy)+'.'+str(self.accuracy)+'f \n'
            f.write(formatting % (self.data['q'][i], self.data['i'][i], self.data['errors'][i]))        
        f.close()
        Logger.log(self.datName, "DatFile Written")


        
#test
if __name__ == "__main__":
    data = { 'q' : [0, 1, 4, 5, 6, 8], 'i' : [ 8, 5, 7, 7, 6, 7], 'errors' : [1, 3, 5, 6, 3, 5, 7]}
    testWrite = DatFileWriter()
    testWrite.writeFile("unittests/", "test.dat", data)