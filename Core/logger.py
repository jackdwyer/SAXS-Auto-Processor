import datetime

def logger(name, message):
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
    logger("Jack", "UNIT TEST MESSAGE")
    logger("Engine", "Engine Started")
    logger("WorkerBufferAverage", "Generated")
    logger("WorkerStaticImage", "Generated")
    logger("WorkerRollingAverageSubtraction", "Generated")
    logger("Engine", "Connected -> BufferRequest")

