def fileWatcher(self, filename):
       start_time = time.time()
       time.sleep(1.0) # wait a lil bit as i know its not there straight away
       while not os.path.isfile(filename):
           print "Waiting for: %s" % filename
           time.sleep(0.1)
           if time.time()-start_time > 30.0: 
               print "Timeout waiting for: %s" % filename 
               return
       print "Got file: %s" % filename
       self.goodFile.value = bytearray(filename) + bytearray(b"\x00"*256)
       self.publisher.send("IMAGE " + pickle.dumps({'image': filename}))
 