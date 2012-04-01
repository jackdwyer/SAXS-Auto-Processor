"""
21/02/2012
Jack Dwyer

Class for processing a single line off the logfile
"""

#TODO: should only get the attributes when needing to generate sql DB, then should just pass it the list
#to grab only the values that are required in the list

import xml.etree.ElementTree 
class LogLine:    
    
    def __init__(self, line):
        self.line = line
        self.xmlify()
        self.attributes = []
        self.data = {}
        self.getAttributes()
        self.getValueDict(self.attributes)
        
    
    def xmlify(self):
        """makes the logline into and pesudo xml file, which we can access using
        xml.etree.element library"""
        self.line = "<?xml version='1.0'?><root>%s</root>" % self.line
        self.line = xml.etree.ElementTree.fromstring(self.line)
        
        #Example of line after its been wrapped to be used as an xml string:
        #<?xml version='1.0'?><root><LOGLINE TimeStamp = 'Thu Feb 09 2012 11:44:51.659' NumericTimeStamp = '110162691.659' exptime = '1' Energy = '12' Temp1 = '-273.15' >/home/det/p2_det/images/data/Cycle_2012_1/Sarrac_4661/lineup_1_0001.tif</LOGLINE></root>

    def getAttributes(self):
        """Gets all the attributes from the line  """
        attribList = []
        for el in self.line:
            for p in el.attrib:
                if p not in attribList:
                    attribList.append(p)
        x = 'ImageLocation'
        attribList.append(x)
        self.attributes = attribList
        


    def getValueDict(self, attributeList):
        """Generates a dictionary of Key(the attribute name) : value """
        for el in self.line:
            for i in range(len(attributeList)):
                if (attributeList[i] == "ImageLocation"): #this needs to be here as imagelocation has to be forced as its element.text
                    self.data[attributeList[i]] = el.text
                else:
                    self.data[attributeList[i]] = el.attrib[attributeList[i]]
        #self.data['ImageLocation'] = el.text

    def getValue(self, attribute):
        """Can just use eg:x logObject.data['value'] instead of calling this method """
        return self.data[attribute]
                

if __name__ == "__main__":
    line = '<LOGLINE TimeStamp = "Sun Apr 01 2012 17:25:45.715" NumericTimeStamp = "114679545.715" exptime = "1" SampleTableX = "0" SampleTableY = "-0.00204353" Energy = "12" Temperature1 = "30.548" Temperature2 = "-270" WellNumber = "19" SampleType = "0" WashType = "0" FilePluginDestination = "all" FilePluginFileName = "/home/det/p2_det/images/data/Cycle_2012_1/Melton_4615/P1B7_HCL_PH3_100_NACL_0586.tif" NORD = "9" Ibs = "31460" I0 = "59688" It = "0" >/home/det/p2_det/images/data/Cycle_2012_1/Melton_4615/P1B7_HCL_PH3_100_NACL_0586.tif</LOGLINE>'
    a = LogLine(line)
    #print a.line
    #a.getAttributes()
    #print a.data
    print a.attributes
    print a.data["SampleType"]
    
                
