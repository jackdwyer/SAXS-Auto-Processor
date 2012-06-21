import xml.etree.ElementTree 

class LogLine:    
    """
    .. codeauthor:: Jack Dwyer <jackjack.dwyer@gmail.com>
    Class for parsing each log line into an XML format so to all easy data retrieval 
    Args:
        line (String): the logline that you want to parse
    """
    
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
        """
        Gets all the attributes from the line to then be used to match up an element dictionary
        """
        attribList = []
        for el in self.line:
            for p in el.attrib:
                if p not in attribList:
                    attribList.append(p)
        x = 'ImageLocation'
        attribList.append(x)
        self.attributes = attribList
        


    def getValueDict(self, attributeList):
        """
        | Generates a dictionary of Key(the attribute name) : value 
        | ImageLocation is manually added as it falls out of the auto generated xml scope
        """
        for el in self.line:
            for i in range(len(attributeList)):
                if (attributeList[i] == "ImageLocation"): #this needs to be here as imagelocation has to be forced as its element.text
                    self.data[attributeList[i]] = el.text
                else:
                    self.data[attributeList[i]] = el.attrib[attributeList[i]]
        #self.data['ImageLocation'] = el.text

    def getValue(self, attribute):
        """Can just use eg:x logObject.data['value'] instead of calling this method 
        
        Returns:
            The 'value' specified
        """
        return self.data[attribute]
                

if __name__ == "__main__":
    lineNew = '<LOGLINE TimeStamp = "Wed May 23 2012 16:18:33.038" NumericTimeStamp = "119168313.038" ImageCounter = "1" exptime = "1.000000" SampleTableX = "0.000000" SampleTableY = "0.000000" Energy = "12.000001" Temperature1 = "27.170000" Temperature2 = "-270.000000" WellNumber = "1.000000" SampleType = "1" WashType = "3" SamplePhi = "1.000000" SampleOmega = "-0.085000" SampleChi = "1.400000" SampleX = "208.015625" SampleY = "-7.210000" FilePluginDestination = "FileLOGWRITER1 FileASCII1" FilePluginFileName = "/home/det/p2_det/images/data/Cycle_2012_2/Devlin_5155A/images/dark_5_0018.tif" NORD = "0" Ibs = "0" I0 = "0" It = "0" >/home/det/p2_det/images/data/Cycle_2012_2/Devlin_5155A/images/dark_5_0018.tif</LOGLINE>'
	
    line = '<LOGLINE TimeStamp = "Sun Apr 01 2012 17:25:45.715" NumericTimeStamp = "114679545.715" exptime = "1" SampleTableX = "0" SampleTableY = "-0.00204353" Energy = "12" Temperature1 = "30.548" Temperature2 = "-270" WellNumber = "19" SampleType = "0" WashType = "0" FilePluginDestination = "all" FilePluginFileName = "/home/det/p2_det/images/data/Cycle_2012_1/Melton_4615/P1B7_HCL_PH3_100_NACL_0586.tif" NORD = "9" Ibs = "31460" I0 = "59688" It = "0" >/home/det/p2_det/images/data/Cycle_2012_1/Melton_4615/P1B7_HCL_PH3_100_NACL_0586.tif</LOGLINE>'
    a = LogLine(lineNew)
    #print a.line
    #a.getAttributes()
    #print a.data
    print a.attributes
    print a.data["SampleType"]
    
                
