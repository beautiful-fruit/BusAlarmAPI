from sqlalchemy import select, func

from main import Stops, EstimatedTimes, StopOfRoutes


def get_nearest_stops(session, lat, long, limit=5):
    # Haversine formula to calculate distance
    distance = func.sqrt(
        func.pow((Stops.latitude - lat), 2) + func.pow((Stops.longitude - long), 2)
    )
    stmt = select(Stops).order_by(distance).limit(limit)
    return session.exec(stmt).all()

def get_routes_between_stops(session, start_stop_ids, end_stop_ids):
    # 找出同一條路線且direction相同，且start_stop的stopSequence < end_stop的stopSequence
    stmt = (
        select(
            StopOfRoutes.routeId,
            StopOfRoutes.direction,
            StopOfRoutes.stopId,
            StopOfRoutes.stopSequence
        )
        .where(start_stop_ids <= StopOfRoutes.stopId <= end_stop_ids)
    )
    results = session.exec(stmt).all()
    # 進一步處理，找出同一條routeId、direction下，start_stop的stopSequence < end_stop的stopSequence
    route_candidates = []
    for start in results:
        if start.stopId not in start_stop_ids:
            continue
        for end in results:
            if (
                end.stopId in end_stop_ids
                and start.routeId == end.routeId
                and start.direction == end.direction
                and start.stopSequence < end.stopSequence
            ):
                route_candidates.append({
                    "routeId": start.routeId,
                    "direction": start.direction,
                    "start_stopId": start.stopId,
                    "start_seq": start.stopSequence,
                    "end_stopId": end.stopId,
                    "end_seq": end.stopSequence,
                })
    return route_candidates

def get_next_buses(session, route_candidates, time, limit=5):
    buses = []
    for candidate in route_candidates:
        stmt = (
            select(EstimatedTimes)
            .where(
                EstimatedTimes.routeId == candidate["routeId"],
                EstimatedTimes.direction == candidate["direction"],
                EstimatedTimes.stopId == candidate["start_stopId"],
                EstimatedTimes.estimatedTime >= time
            )
            .order_by(EstimatedTimes.estimatedTime)
            .limit(1)
        )
        result = session.exec(stmt).first()
        if result:
            buses.append({
                "routeId": candidate["routeId"],
                "direction": candidate["direction"],
                "start_stopId": candidate["start_stopId"],
                "end_stopId": candidate["end_stopId"],
                "estimatedTime": result.estimatedTime
            })
    # 按照estimatedTime排序，取前五
    buses.sort(key=lambda x: x["estimatedTime"])
    return buses[:limit]
