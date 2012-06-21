import DatFile
import glob

class OutLierRejection():
    """
    .. codeauthor:: Jack Dwyer <jackjack.dwyer@gmail.com>
    A class that takes a list of DatFiles and changes the reference Valid value to True or False, based on Nathan Cowieson's Algorithm
    """
    
    def __init__(self):
        print "out lier rejection created"

    def process(self, datFiles):
        """ 
        Takes the list of datFiles and processses their high/low Q's and checks validity
        
        Args:
            datFiles (list[] of DatFile objects)
            
        Returns:
            Nothing
        
        Sets the reference valid value to True or False of the DatFile
        """
        if (len(datFiles) == 1 or len(datFiles) == 0):
            return False
        else:
            ILQ = []
            IHQ = []
            for dat in datFiles:
                ILQ.append(dat.getILQ())
                IHQ.append(dat.getIHQ())
                
            ihqThreshold = (0.95 * max(IHQ))
            ilqThreshold = (1.05 * min(ILQ))
            
            print "IQL Threshold: ", str(ilqThreshold)
            print "IHQ Threshold: ", str(ihqThreshold)
            
            for dat in datFiles:
                if ((dat.getIHQ() < ihqThreshold) or (dat.getILQ() > ilqThreshold)):
                    print dat.getFileName()
                    print "FAILED"
                else:
                    print "valid"
                    #print dat.getIHQ()
                    #print dat.getILQ()
                    dat.setValid(True)



if __name__ == '__main__':
    outerlierTest = OutLierRejection()
    print "Running - Outlier Rejection"
    
    datC = glob.glob('testData/35C_naPhos_nacl_ph7c*')
    datD = glob.glob('testData/35C_naPhos_nacl_ph7d*')

    dC = []


    for files in datC:
        dC.append(DatFile.DatFile(files))
    outerlierTest.process(dC)



