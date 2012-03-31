"""
Jack Dwyer
31 March 2012

Common generic averaging class/methods.  

"""

class AverageList:
    
    def __init__(self, list):
        self.outterList = list
        self.accuracy = accuracy
        
    
    
    def average(self):
        if (len(self.outterList) == 1): #Unable to average with only 1 list
            return list
        
        results = []
        v = float(0)
        innerList = self.outterList[0]
        for x in range(len(self.innerList)):
            for i in range(len(self.outterList)):
                v = self.outterList[i][x] + v
            results = append(v)
            v = float(0)
        return results
    
    

        
        