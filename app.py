from Optimize import Alternative, Best
import json
import pandas as pd


while True:
    mode = input("Mode: ")
    league = input("League: ")

    if mode == "all":
        bank = float(input("Bank: "))

        with open("players.json") as json_file:
            data = json.load(json_file)

        players = data[league]

        for player in players:
            alternatives = Alternative(player, league, bank).better_choice()

            nr_alternatives = len(alternatives) - 1 if len(alternatives) > 0 else 0

            print(f"{player}: {nr_alternatives}")

    elif mode == "player":
        bank = float(input("Bank: "))
        player = input("Player: ")
        Alternative(player, league, bank).print_better_choice()

    elif mode == "cost":
        cost = float(input("Cost: "))
        Best(league).for_cost(cost)