
from sqlalchemy import create_engine, Column, Integer, String, JSON, types, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.mysql.base import MSText
from sqlalchemy.orm.session import Session
from sqlalchemy.schema import Column
from sqlalchemy.engine.base import Engine
import uuid

Base = declarative_base()


class Attributes:
    STATUS_IN_PROGRESS = 'in-progress'
    STATUS_DONE = 'success'
    STATUS_FAILURE = 'failure'

class ORM:
    engine: Engine
    session: Session  # type: Session

    def __init__(self, db_string: str):
        self.engine = create_engine(db_string, echo=True)
        self.session = sessionmaker(bind=self.engine, autoflush=False, autocommit=True)()
        Base.metadata.create_all(self.engine)


class UUID(types.TypeDecorator):
    impl = MSText

    def __init__(self):
        self.impl.length = 16
        types.TypeDecorator.__init__(self, length=self.impl.length)

    def process_bind_param(self, value, dialect=None):
        if value and isinstance(value, uuid.UUID):
            return value.bytes.decode('utf-8')
        elif value and not isinstance(value, uuid.UUID):
            return value
        else:
            return None

    def process_result_value(self, value, dialect=None):
        if value:
            return value
        else:
            return None

    def is_mutable(self):
        return False


class Pipeline(Base):
    """ Granted access to execute a single script, with pre-defined environment variables, access code """

    __tablename__ = 'pipeline'

    id = Column(UUID, primary_key=True)
    title = Column(String)
    secret = Column(String)
    script = Column(String)
    params = Column(JSON)
    executions = relationship("Execution", back_populates="pipeline")


class Execution(Base):
    """ Every single execution of a Pipeline """

    __tablename__ = 'execution'

    id = Column(Integer, primary_key=True, autoincrement=True)
    execution_number = Column(Integer, nullable=False)
    invoked_by_ip = Column(String, nullable=False)
    payload = Column(String, nullable=False)
    log = Column(String, nullable=False)
    pipeline_id = Column(Integer, ForeignKey('pipeline.id'))
    pipeline = relationship("Pipeline", back_populates="executions")  # type: Pipeline
    status = Column(String, nullable=False, default=Attributes.STATUS_IN_PROGRESS)

    def to_ident_string(self) -> str:
        return 'pipe_' + self.pipeline.id + '_exec_' + str(self.execution_number)

    def mark_as_finished(self, result: bool, log: str):
        self.log = log
        self.status = Attributes.STATUS_DONE if result else Attributes.STATUS_FAILURE
