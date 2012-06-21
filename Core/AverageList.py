class AverageList:
    """
    .. codeauthor:: Jack Dwyer <jackjack.dwyer@gmail.com>
    An Object that takes a list of lists as the parameter and averages them out
    """
    
    
    def __init__(self, list = []):
        self.outterList = list      
    
    def average(self, list):
        """
        Averages out the lists
        
        Args:
            lists (list of lists)
        
        Return:
            results (lits): the averaged results from the list
        
        Raises:
            IndexError: If the list of lists don't match up
            
        """
        self.outterList = list
        if (len(self.outterList) == 1): #Unable to average with only 1 list
            return list[0] #need this, else it returns a list of lists
        
        results = []
        v = float(0)
        innerList = self.outterList[0]
        for x in range(len(innerList)):
            try:
                for i in range(len(self.outterList)):
                    v = self.outterList[i][x] + v
                v = v / (len(self.outterList))
                results.append(v)
                v = float(0)
            except IndexError:
                pass
        return results
    

#Tests
if __name__ == "__main__":
   
    
    expected1 = 88.4
    expected2 = 60.2
    
    
    l1 = [80, 96]
    l2 = [95, 55]
    l3 = [100, 69]
    l4 = [77, 21]
    l5 = [90, 60]
    
    l = [l1, l2, l3, l4, l5]

    testAverage = AverageList()
    t = testAverage.average(l)
    
    if t[0] == expected1:
        print "PASSED - TEST 1"
    else: 
        print "FAILED - TEST 1"
        print "OUTPUT VALUE = "
        print t[0]
    if t[1] == expected2:
        print "PASSED - TEST 2"
    else:
        print "FAILED - TEST 2"
        print "OUTPUT VALUE = "
        print t[1]

        
        
