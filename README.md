# SAX-Auto-Processor

##Required Third party Libraries
- Mysqldb
- yaml (for reading configuration files)
- epics
- zmq


**Check internal wiki under SAXS-WAXS to get latest install details, when finalised (soon) will place here**


##Live Experiment Usage

WORKERDB - Special Use Case
Details:
Only single instance should only be instantiated by the SAXS-Auto-Processor.


##Messaging Workers:

Format for messaging Workers is a dictionary
The first item is always
{ 'command' : 'command_you_want_to_call' }
You can extend the dictionary with what ever data you want your worker to use.  Everything is sent and received as a python object. Using: send_pyobj(obj), and recv_pyobj(obj)

###Default/Generic Commands
{ 'command' : 'clear'} 
Worker will clear itself

{ 'command' : 'shut_down'}
Worker will shutdown/close all ports 

{ 'command' : 'update_user', 'user' : new_user }

{ 'command' : 'update_user', 'user' : new_user }

{ 'command' : 'absolute_directory', 'absolute_directory' : new_directory }




