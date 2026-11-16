import grpc
import time
from datetime import datetime, timedelta
from concurrent import futures

import football_pb2
import football_pb2_grpc


# Testni podatki o nogometnih tekmah
matches = [
    football_pb2.Match(
        id=1,
        home_team="Arsenal",
        away_team="Chelsea",
        stadium="Emirates Stadium",
        city="London",
        date="2026-12-05",
        time="18:00",
        ticket_price=50.0
    ),
    football_pb2.Match(
        id=2,
        home_team="Maribor",
        away_team="Olimpija",
        stadium="Ljudski vrt",
        city="Maribor",
        date="2026-12-06",
        time="20:00",
        ticket_price=20.0
    ),
    football_pb2.Match(
        id=3,
        home_team="Barcelona",
        away_team="Real Madrid",
        stadium="Camp Nou",
        city="Barcelona",
        date="2026-12-12",
        time="21:00",
        ticket_price=80.0
    )
]


# Pomozna funkcija za iskanje tekme
def find_match(match_id):
    for match in matches:
        if match.id == match_id:
            return match

    return None


# Implementacija gRPC storitve
class FootballService(
    football_pb2_grpc.FootballServiceServicer
):

    # 1. Pridobivanje vseh tekem
    def GetMatches(self, request, context):
        return football_pb2.MatchesResponse(
            matches=matches
        )

    # 2. Pridobivanje podrobnosti tekme
    def GetMatchDetails(self, request, context):
        match = find_match(request.match_id)

        if match is None:
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                "Tekma ne obstaja."
            )

        return football_pb2.MatchResponse(
            match=match
        )

    # 3. Izracun stroska vstopnic
    def CalculateCost(self, request, context):
        match = find_match(request.match_id)

        if match is None:
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                "Tekma ne obstaja."
            )

        if request.number_of_people <= 0:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "Stevilo oseb mora biti pozitivno."
            )

        total_cost = (
            match.ticket_price * request.number_of_people
        )

        return football_pb2.CostResponse(
            ticket_price=match.ticket_price,
            total_cost=total_cost
        )

    # 4. Pretakanje nacrta obiska
    def StreamVisitPlan(self, request, context):
        match = find_match(request.match_id)

        if match is None:
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                "Tekma ne obstaja."
            )

        match_time = datetime.strptime(
            match.time, "%H:%M"
        )

        arrival_time = (
            match_time - timedelta(hours=1)
        ).strftime("%H:%M")

        steps = [
            f"Tekma: {match.home_team} - {match.away_team}",
            f"Mesto: {match.city}",
            f"Stadion: {match.stadium}",
            f"Datum tekme: {match.date}",
            f"Zacetek tekme: {match.time}",
            f"Priporocen prihod: {arrival_time}",
            f"Cena vstopnice: {match.ticket_price:.2f} EUR",
            "Nacrt obiska je pripravljen."
        ]

        for step in steps:
            yield football_pb2.VisitResponse(
                step=step
            )

            time.sleep(1)


# Zagon streznika
def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10)
    )

    football_pb2_grpc.add_FootballServiceServicer_to_server(
        FootballService(),
        server
    )

    server.add_insecure_port("localhost:50051")

    server.start()

    print("gRPC streznik deluje na vratih 50051.")

    server.wait_for_termination()


if __name__ == "__main__":
    serve()