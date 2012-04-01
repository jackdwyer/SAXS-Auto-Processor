def log(name, message):
    formatting  = '%s %15s %10s'
    print(formatting % ('['+name+']','--', message)) #Needed for string formatting