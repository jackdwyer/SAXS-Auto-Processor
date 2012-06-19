from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String


class TableBuilder():

    def __init__(self, database, tableName, attribList):
        self.Base = declarative_base()
        self.tableName = tableName
        #self.engine = create_engine('sqlite:///'+str(location)+str(user)+'.db')
        self.engine = create_engine("mysql+mysqldb://root:a@localhost/"+database)
        self.dictColumns = {}
        self.attribList = self.columnBuilder(attribList)
        self.table = self.gen(self.tableName, self.dictColumns)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
    
    def gen(self, table_name, colDict):
        class logDataTableBuilder(self.Base):
            locals().update(colDict)  
            __tablename__ = table_name
            id = Column(Integer, primary_key=True)
    
        self.Base.metadata.create_all(self.engine)
        return logDataTableBuilder

    def columnBuilder(self, attribList):
        for attribute in attribList:
            self.dictColumns[attribute] = Column(String(250))
                 
    def addData(self, data):
        newData = self.table(**data)
        self.session.add(newData)
        self.session.commit()
        

if __name__ == "__main__":
    
    print "winner"
    collumAttributes = ['WashType', 'SampleOmega', 'FilePluginDestination', 'Temperature2', 'Temperature1', 'WellNumber', 'SamplePhi', 'NumericTimeStamp', 'I0', 'SampleY', 'SampleX', 'SampleChi', 'TimeStamp', 'SampleType', 'ImageCounter', 'Ibs', 'exptime', 'FilePluginFileName', 'Energy', 'It', 'SampleTableX', 'SampleTableY', 'NORD', 'ImageLocation']
    t = TableBuilder("JAck", "images", collumAttributes)

    
     
    
