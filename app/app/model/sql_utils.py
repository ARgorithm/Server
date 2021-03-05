import enum
from sqlalchemy import Column, String, LargeBinary , Boolean , DateTime , ForeignKey , Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ProgrammerDB(Base):
    __tablename__ = "programmer"

    email = Column('email',String , primary_key=True)
    password = Column('password',String)
    public_id = Column('public_id',String , index=True)
    admin = Column('admin',Boolean)
    confirmed = Column('confirmed',Boolean)
    black_list = Column('black_list',Boolean)
    join_date = Column('join_date',DateTime)

class UserDB(Base):
    __tablename__ = "user"

    email = Column('email',String , primary_key=True)
    password = Column('password',String)
    public_id = Column('public_id',String , index=True)
    black_list = Column('black_list',Boolean)

class ARgorithmDB(Base):
    __tablename__ = "argorithm"
    
    maintainer = Column('maintainer',ForeignKey("programmer.email", ondelete="CASCADE"),nullable=False)
    argorithmID = Column('argorithmID',String , primary_key=True)
    filename = Column('filename',String)
    function = Column('function',String,nullable=False)
    parameters = Column('parameters',String)
    example = Column('example',String)
    description = Column('description',String)
    filedata = Column('filedata',LargeBinary , default=None)

    programmer = relationship(ProgrammerDB)

class ReportType(enum.Enum):
    User = 1
    System = 2
    Alert = 3

class BugReports(Base):
    __tablename__ = "reports"

    argorithmID = Column('argorithm_id' , ForeignKey('argorithm.argorithmID', ondelete="CASCADE"),nullable=False)
    report_id = Column('report_id',String , primary_key = True)
    bug_type = Column('bug_type',Enum(ReportType),nullable=False)
    timestamp = Column('timestamp', DateTime)
    checked = Column('checked' , Boolean)
    description = Column('description',String)

    argorithm = relationship(ARgorithmDB)


