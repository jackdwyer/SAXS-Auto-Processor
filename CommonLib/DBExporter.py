"""
22/02/2012
Jack Dwyer

Class for wrapping the SQL alchemy commands for entering data into the database
- Will also create a table for new experiments
- auto generate the sessions

"""

"""
TODO: Work out the table structure.. as I can't make a db until i have read the first line of the log file
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base





"""
TODO: Generate the connection string on the based on parameters supplied 


MAKE A DB BASED ON THE NAME.. then the next directory will be the table
"""

class DBExporter:
    
    def __init__(self, user, experiment):
        self.name = "DBExporter"
        #here could generate connection string on the fly, needed for take home if they are going to be connecting to SQLite
        db = "mysql+mysqldb://root:a@localhost/"+user
        engine = create_engine(db)

        Base = declarative_base()

        class Table(Base):
            __tablename__ = "name"
            id = Column(Integer, primary_key = True)
            name = Column(String)
        
        Base.metadata.create_all(engine)
              
        
        
if __name__ == "__main__":
    testDB = DBExporter()
    print testDB
    
    connection = testDB.engine.connect()
    result = connection.execute("select * from SAMPLE_TYPE")
    for row in result:
        print row