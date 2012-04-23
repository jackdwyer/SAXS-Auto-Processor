def log(name, message):
    formatting  = '%34s %10s %1s'
    print(formatting % ('['+name+']','--', message)) #Needed for string formatting