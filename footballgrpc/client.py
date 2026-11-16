import grpc

import football_pb2
import football_pb2_grpc


# 1. Pridobivanje vseh tekem
def get_matches(stub):
    response = stub.GetMatches(
        football_pb2.MatchesRequest()
    )

    print("\nSeznam nogometnih tekem:")

    for match in response.matches:
        print(
            f"{match.id}. {match.home_team} - "
            f"{match.away_team} ({match.date})"
        )


# 2. Pridobivanje podrobnosti tekme
def get_match_details(stub):
    match_id = int(input("Vnesi ID tekme: "))

    request = football_pb2.MatchRequest(
        match_id=match_id
    )

    response = stub.GetMatchDetails(request)

    match = response.match

    print("\nPodrobnosti tekme:")
    print(f"Domaca ekipa: {match.home_team}")
    print(f"Gostujoca ekipa: {match.away_team}")
    print(f"Stadion: {match.stadium}")
    print(f"Mesto: {match.city}")
    print(f"Datum: {match.date}")
    print(f"Ura: {match.time}")
    print(f"Cena vstopnice: {match.ticket_price:.2f} EUR")


# 3. Izracun stroska vstopnic
def calculate_cost(stub):
    match_id = int(input("Vnesi ID tekme: "))
    number_of_people = int(input("Vnesi stevilo oseb: "))

    request = football_pb2.CostRequest(
        match_id=match_id,
        number_of_people=number_of_people
    )

    response = stub.CalculateCost(request)

    print("\nIzracun stroska:")
    print(f"Cena vstopnice: {response.ticket_price:.2f} EUR")
    print(f"Skupni strosek: {response.total_cost:.2f} EUR")


# 4. Pretakanje nacrta obiska
def stream_visit_plan(stub):
    match_id = int(input("Vnesi ID tekme: "))

    request = football_pb2.VisitRequest(
        match_id=match_id
    )

    responses = stub.StreamVisitPlan(request)

    print("\nNacrt obiska nogometne tekme:")

    for response in responses:
        print(response.step, flush=True)


# Konzolni meni
def main():

    with grpc.insecure_channel("localhost:50051") as channel:

        stub = football_pb2_grpc.FootballServiceStub(
            channel
        )

        while True:

            print("\n=== NACRTOVALEC OBISKA NOGOMETNE TEKME ===")
            print("1. Prikazi vse tekme")
            print("2. Prikazi podrobnosti tekme")
            print("3. Izracunaj strosek vstopnic")
            print("4. Pripravi nacrt obiska tekme")
            print("0. Izhod")

            choice = input("Izberi moznost: ")

            try:
                if choice == "1":
                    get_matches(stub)

                elif choice == "2":
                    get_match_details(stub)

                elif choice == "3":
                    calculate_cost(stub)

                elif choice == "4":
                    stream_visit_plan(stub)

                elif choice == "0":
                    print("Konec programa.")
                    break

                else:
                    print("Neveljavna izbira.")

            except ValueError:
                print("Napaka: vnesi celo stevilo.")

            except grpc.RpcError as error:
                print(f"Napaka gRPC: {error.details()}")


if __name__ == "__main__":
    main()