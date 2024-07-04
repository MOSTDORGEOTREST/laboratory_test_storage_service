from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    BigInteger,
    Integer,
    DateTime,
    Index
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.database import Base

class Objects(Base):
    __tablename__ = "objects"

    object_id = Column(String(32), primary_key=True, comment='from EngGeo')
    object_number = Column(String(10), unique=True)
    description = Column(String(500), default=None)

    boreholes = relationship("Boreholes")

class Boreholes(Base):
    __tablename__ = "boreholes"

    borehole_id = Column(String(32), primary_key=True, comment='from EngGeo')
    borehole_name = Column(String(50))
    object_id = Column(String(32), ForeignKey('objects.object_id'), index=True)
    description = Column(String(500), default=None)

    samples = relationship("Samples")

class Samples(Base):
    __tablename__ = "samples"

    sample_id = Column(String(32), primary_key=True, comment='from EngGeo')
    borehole_id = Column(String(32), ForeignKey('boreholes.borehole_id'), index=True)
    laboratory_number = Column(String(50))
    soil_type = Column(String(500))
    properties = Column(JSONB, nullable=True, default=None)
    description = Column(String(500), default=None)

    tests = relationship("Tests")

class Tests(Base):
    __tablename__ = "tests"

    test_id = Column(BigInteger, primary_key=True, autoincrement=True)
    sample_id = Column(String(32), ForeignKey('samples.sample_id'), index=True)
    test_type_id = Column(Integer, ForeignKey('test_types.test_type_id'), index=True)
    timestamp = Column(DateTime, server_default=func.now())
    test_params = Column(JSONB, nullable=True, default=None)
    test_results = Column(JSONB, nullable=True, default=None)
    description = Column(String(500), default=None)

    files = relationship("Files")

class TestTypes(Base):
    __tablename__ = "test_types"

    test_type_id = Column(Integer, primary_key=True, autoincrement=True)
    test_type = Column(String(500), unique=True)
    description = Column(String(500), default=None)

class Files(Base):
    __tablename__ = "files"

    file_id = Column(BigInteger, primary_key=True, autoincrement=True)
    test_id = Column(BigInteger, ForeignKey('tests.test_id'), index=True)
    upload = Column(DateTime, server_default=func.now())
    key = Column(String(500))
    description = Column(String(500), default=None)

class ParametersTitles(Base):
    __tablename__ = "parameters_titles"

    param_id = Column(BigInteger, primary_key=True, autoincrement=True)
    param_name = Column(String(50))
    param_title = Column(String(500))
    description = Column(String(500), default=None)

ix_tests_timestamp = Index('ix_tests_timestamp', Tests.timestamp, postgresql_using='btree')

