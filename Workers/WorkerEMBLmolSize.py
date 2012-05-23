import sys, subprocess
from Worker import Worker

from Core.Logger import log

""" Dat file needed is in relative location
sub/raw_sub

"""

class WorkerEMBLmolSize(Worker):
    
    def __init__(self):
        Worker.__init__(self, "WorkerEMBLmolSize")


    def connect(self, pullPort, dbPushPort):
        self.pull.bind("tcp://127.0.0.1:"+str(pullPort))
        if (dbPushPort):
            self.dbPush.connect("tcp://127.0.0.1:"+str(dbPushPort))
            log(self.name, "All Ports Connected -> pullPort: "+str(pullPort) + " -> dbPushPort: "+str(dbPushPort))
        else:
            log(self.name, "All Ports Connected -> pullPort: "+str(pullPort))
        
        self.run()
    
    def process(self, test):  
        if (str(test) == "subtracted_dat"):
            datFile = self.pull.recv()
            log(self.name, "About to process DatFile: " + str(datFile))
            self.processDatFile(datFile)  



    def processDatFile(self, datFile):
        """
        process = subprocess.Popen(['autorg', '-f', 'ssv', str(datFile)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output,errorOutput = process.communicate()
        
        print output
        
        valuePoints = output.split(" ")
        rg = valuePoints[0]
        
        process = subprocess.Popen(['datgnom', '-r', str(rg), '-s', '12', str(datFile)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output,errorOutput = process.communicate()
        
        print output
        
        process = subprocess.Popen(['datporod', 'sample_data/sum_data_4.out'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output,errorOutput = process.communicate()
        
        print output       
        """
        print "in PROCESS DAT FILE FUNCTION, this needs to get correct directory"
        print "THE DAT FILE IS: " + str(datFile)    
        f = datFile.split(".")
        print "the the enw file will be called: " + str(f[0]) + ".out"                             