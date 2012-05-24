"""
Jack Dwyer
Outlier rejection
pass a list of average high Q and averaged low Q.

Will need to pass a dictionary of all dat files to be checked against
"""

import DatFile

class OutLierRejection():
    def __init__(self):
        print "out lier rejection created"

    def process(self, datFiles):
        #If length is 1, can not check
        if (len(datFiles) == 1):
            return False
        else:
            print "iql"
            for dat in datFiles:
#                IQL 




if __name__ == '__main__':
    print "Running - Outlier Rejection"
    dat1 = DatFile.DatFile("testData/empty_cap2a_chk_0001.dat")
    dat2 = DatFile.DatFile("testData/empty_cap2a_chk_0002.dat")
    dat3 = DatFile.DatFile("testData/empty_cap2a_chk_0003.dat")
    dat4 = DatFile.DatFile("testData/empty_cap2a_chk_0004.dat")
    
    o = OutLierRejection()
    o.process([dat1, dat2, dat3, dat4])
    
    print dat1.findILQ()
    print dat2.findILQ()
    print dat3.findILQ()
    print dat4.findILQ()