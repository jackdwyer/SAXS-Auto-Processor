"""
Jack Dwyer
12/04/2012
Will be super class for all workers

Will also be abstract/interface for what methods need to be overridden etc
"""


import zmq



class Worker:
    
    def __init__(self):
        self.port = ""
        
        self.context = zmq.Context()
        self.pull = self.context.socket(zmq.PULL)
        
    
    def connect(self, port):
        self.pull.connect("tcp://127.0.0.1:"+str(port))

    #TODO: rename to clear, and drop into all workers
    def clear1(self):
        
        
        #Clear all lists TODO dictionaries/variables
        for i in range(len(self.dataList)):
            self.dataList[i] = []
        print self.dataList
        
    

if __name__ == "__main__":
    a = Worker()
    a.clear() 