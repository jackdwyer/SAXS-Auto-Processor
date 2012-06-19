from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String



class Database():
    
    def __init__(self, user, location):
        self.base = declarative_base()
        self.engine = self.createEngine(user, location)            

    def createEngine(self, user, location):
        return create_engine('sqlite:///'+location+"/"+user+".db")
    
    
    def gen(self, table_name, list):
        colDict = self.columnBuilder(list)
        
        class logDataTableBuilder(self.base):
            locals().update(colDict)  
            __tablename__ = table_name
            id = Column(Integer, primary_key=True)
    
        self.base.metadata.create_all(self.engine)
        return logDataTableBuilder

    def columnBuilder(self, attribList):
        dictColumns = {}
        for attribute in attribList:
            dictColumns[attribute] = Column(String(250))
        return dictColumns 
                
    def addData(self, data):
        newData = self.table(**data)
        self.session.add(newData)
        self.session.commit()