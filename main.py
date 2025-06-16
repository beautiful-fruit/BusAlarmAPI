from fastapi import FastAPI
from typing import Optional
from sqlmodel import SQLModel, Field, create_engine
import datetime
from typing import List
import strawberry
from fastapi import HTTPException
from sqlmodel import Session, select

from util import get_nearest_stops, get_routes_between_stops, get_next_buses


# database schema
class Routes(SQLModel, table=True):
    routeId: int = Field(primary_key=True, index=True)
    routeName: str
    direction: int
    headsign: str


class Stops(SQLModel, table=True):
    stopId: int = Field(primary_key=True, index=True)
    stopName: str
    latitude: float
    longitude: float


class StopOfRoutes(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    routeId: int = Field(foreign_key="routes.routeId")
    direction: int
    stopId: int = Field(foreign_key="stop.stopId")
    stopSequence: int


class EstimatedTimes(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    routeId: int = Field(foreign_key="routes.routeId")
    direction: int
    stopId: int = Field(foreign_key="stop.stopId")
    estimatedTime: int


engine = create_engine("sqlite:///./database.db", echo=True)
SQLModel.metadata.create_all(engine)

@strawberry.type(name="Routes")
class RoutesType:
    routeId: int
    routeName: str
    direction: int
    headsign: str


@strawberry.type
class StopsType:
    stopId: int
    stopName: str
    latitude: float
    longitude: float


@strawberry.type
class StopOfRoutes:
    id: int
    routeId: int
    direction: int
    stopId: int
    stopSequence: int


@strawberry.type
class ListOfStopsType:
    stops: List[StopsType]


@strawberry.type
class EstimatedTimes:
    id: int
    routeId: str
    direction: int
    stopId: str
    estimatedTimes: datetime.datetime

@strawberry.type
class ListOfAllBus:
    routeId: int
    direction: int
    start_stopId: int
    end_stopId: int
    estimatedTimes: datetime.datetime


@strawberry.type
class Query:
    @strawberry.field
    def all_stops(self) -> ListOfStopsType:
        with Session(engine) as session:
            stops = session.exec(select(Stops)).all()
            if len(stops) == 0:
                raise HTTPException(status_code=404, detail="No stop found")
            return ListOfStopsType(stops=[
                StopsType(
                    stopId=it.stopId,
                    stopName=it.stopName,
                    latitude=it.latitude,
                    longitude=it.longitude
                ) for it in stops
            ]
            )

    @strawberry.field
    def all_routes(
            self,
            start_lat: int,
            start_long: int,
            end_lat: int,
            end_long: int,
            time: datetime.datetime,
            limit: int = 5
    ) -> ListOfStopsType:
        with Session(engine) as session:
            start_stops = get_nearest_stops(session, start_lat, start_long)
            end_stops = get_nearest_stops(session, end_lat, end_long)
            start_stop_ids = [s.stopId for s in start_stops]
            end_stop_ids = [s.stopId for s in end_stops]
            route_candidates = get_routes_between_stops(session, start_stop_ids, end_stop_ids)
            top5_buses = get_next_buses(session, route_candidates, time)
            return top5_buses


app = FastAPI()
