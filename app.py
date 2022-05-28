from Optimize import Alternative, BestPlayer, AllPlayers
from Download import PlayerDownload


league = input("League: ")
bank = float(input("Bank: "))

while True:
    mode = input("Mode (all, player, cost, compare, update): ")

    if mode == "all":
        AllPlayers(league, bank).alternatives()

    elif mode == "player":
        player = input("Player: ")
        Alternative(player, league, bank).print_better_choice()

    elif mode == "cost":
        cost = float(input("Cost: "))
        BestPlayer(league).for_cost(cost)

    elif mode == "compare":
        players = input("Players (,): ").split(",")
        BestPlayer(league).compare_players(players)

    elif mode == "update":
        PlayerDownload(league).download()
        print("Update done!")
