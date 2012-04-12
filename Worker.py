"""
Will be super class for all workers
"""



class Worker:
    
    def run(self):
        print "run"

    def test(self):
        print "test inheritied"


if __name__ == "__main__":
    a = Worker()
    a.run() 