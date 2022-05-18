from Optimize import Alternative
import json
import pandas as pd


while True:
    mode = input("Mode: ")
    league = input("League: ")
    bank = float(input("Bank: "))

    if mode == "all":
        with open("players.json") as json_file:
            data = json.load(json_file)

        players = data[league]

        for player in players:
            alternatives = Alternative(player, league, bank).better_choice()

            nr_alternatives = len(alternatives)-1 if len(alternatives) > 0 else 0

            print(f"{player}: {nr_alternatives}")

    elif mode == "player":
        player = input("Player: ")
        Alternative(player, league, bank).print_better_choice()
