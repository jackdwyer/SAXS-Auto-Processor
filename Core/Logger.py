import datetime

def log(name, message):
    now = datetime.datetime.now()
    
    
    
    logFile = "engine.log"
    formatting  = '%26s %0s %10s %100s'
    #print str(now)
    print "%26s -- [%40s] %10s %s" % (str(now), name, "--", 
                                    message)
    #print formatting % (str(now), ' -- ['+name+']','--', message+"\n"),
    #f = open(logFile, 'a')
    #f.write(formatting % (str(now), '-- ['+name+']','--', message+"\n"))#Needed for string formatting

if __name__ == "__main__":
    log("Jack", "UNIT TEST MESSAGE")
    log("Engine", "Engine Started")
    log("WorkerBufferAverage", "Generated")
    log("WorkerStaticImage", "Generated")
    log("WorkerRollingAverageSubtraction", "Generated")
    log("Engine", "Connected -> BufferRequest")

