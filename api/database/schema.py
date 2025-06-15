from sqlalchemy import create_engine, Column, String, Integer, Double
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./database.db"
engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# database schema
class Routes(Base):
    __tablename__ = "Routes"
    routeId = Column(String, primary_key=True, index=True)
    routeName = Column(String)
    direction = Column(Integer)
    headsign = Column(String)


class Stop(Base):
    __tablename__ = "Stops"
    stopId = Column(String, primary_key=True, index=True)
    stopName = Column(String)
    latitude = Column(Double)
    longitude = Column(Double)


class StopOfRoutes(Base):
    __tablename__ = "StopOfRoutes"
    id = Column(Integer, primary_key=True, index=True)
    routeId = Column(String)
    direction = Column(Integer)
    stopId = Column(String)
    stopSequence = Column(Integer)


class EstimatedTimes(Base):
    __tablename__ = "EstimatedTimes"
    id = Column(Integer, primary_key=True, index=True)
    routeId = Column(String)
    direction = Column(Integer)
    stopId = Column(String)
    estimatedTime = Column(Integer)


Base.metadata.create_all(bind=engine)




