# SAX-Auto-Processor

##Required Third party Libraries
* Mysqldb
* yaml (maybe)
* epics
* zmq
* msgpack (maybe)

**Check internal wiki under SAXS-WAXS to get latest install details, when finalised (soon) will place here **


*Live Experiment Usage*

WORKERDB - Special Use Case
Details:
WorkerDB should utilise the singleton pattern with only one instance being used for inserting/updating/deleting any data inside the current user database.
This single instance should only be instantiated by the SAXS-Auto-Processor.


//Messaging Workers:
Format for messaging Workers is a dictionary
The first item is always
{ 'command' : 'command_you_want_to_call' }
You can extend the dictionary with what ever data you want your worker to use.  Everything is sent and received as a python object. Using: send_pyobj(obj), and recv_pyobj(obj)

Default/Generic Commands
{ 'command' : 'update_user', 'user' : The new user name string }


#Specific Commands
