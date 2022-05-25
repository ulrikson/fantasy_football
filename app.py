from Optimize import Alternative, Best
from Download import PlayerDownload, FixtureDownload
import json


league = input("League: ")
bank = float(input("Bank: "))

while True:
    mode = input("Mode (all, player, cost, compare, update): ")

    if mode == "all":
        with open("data/players.json") as json_file:
            data = json.load(json_file)

        players = data[league]

        for player in players:
            alternatives = Alternative(player, league, bank).better_choice()

            nr_alternatives = len(alternatives) - 1 if len(alternatives) > 0 else 0

            print(f"{player}: {nr_alternatives}")

    elif mode == "player":
        player = input("Player: ")
        Alternative(player, league, bank).print_better_choice()

    elif mode == "cost":
        cost = float(input("Cost: "))
        Best(league).for_cost(cost)

    elif mode == "compare":
        players = input("Players (,): ").split(",")
        Best(league).compare_players(players)

    elif mode == "update":
        FixtureDownload(league).download()
        PlayerDownload(league).download()
        print("Update done!")
