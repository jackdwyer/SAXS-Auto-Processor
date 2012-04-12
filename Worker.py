"""
Jack Dwyer
12/04/2012
Will be super class for all workers

Will also be abstract/interface for what methods need to be overridden etc
"""



class Worker:

    #TODO: rename to clear, and drop into all workers
    def clear1(self):
        
        #Clear all lists TODO dictionaries/variables
        for i in range(len(self.dataList)):
            self.dataList[i] = []
        print self.dataList
        
    

if __name__ == "__main__":
    a = Worker()
    a.clear() 