from black import diff
import requests
import pandas as pd
import json


class FDR:
    def __init__(self, league, gw):
        self.league = league
        self.fixtures_df = pd.read_csv("data/fixtures_" + league + ".csv")
        self.gw = gw

    def get_fdr_next(self, team):
        df = self.fixtures_df
        match = df[(df["team_a"] == team) | (df["team_h"] == team)]

        team_ground = self.__get_team_ground(match)
        is_home = team_ground["home"] == team

        opponent = team_ground["away"] if is_home else team_ground["home"]
        difficulty = self.__get_difficulty(opponent, is_home)

        print(difficulty)

    def __get_team_ground(self, match):
        return {
            "home": match["team_h"].loc[match.index[0]],
            "away": match["team_a"].loc[match.index[0]],
        }

    def __get_difficulty(self, opponent, is_home):
        with open("data/team_difficulty.json") as json_file:
            data = json.load(json_file)

        difficulty = data[self.league][opponent]

        difficulty = difficulty * 1.5 if not is_home else difficulty

        return difficulty


FDR("fal", 10).get_fdr_next("IFK Göteborg")
