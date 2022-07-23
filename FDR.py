import pandas as pd
import json


class FDR:
    def __init__(self, league):
        self.league = league
        self.fixtures_df = pd.read_csv("data/fixtures_" + league + ".csv")
        self.gw = self.__get_gw()
        self.teams = self.__get_teams()
        self.gws_ahead = 5

    def update_fdrs(self, players_df):
        df = players_df
        df["fdr"] = ""

        teams = list(self.teams.keys())
        for team in teams:
            difficulties = self.__get_fdr_next(team)

            players_in_team = df["team"] == team
            df.loc[players_in_team, "fdr"] = difficulties

        return df

    def __get_fdr_next(self, team):
        difficulties = []
        for gw in range(self.gw, self.gw + self.gws_ahead):
            match = self.__get_match(team, gw)

            if len(match.index) == 0:
                continue

            team_ground = self.__get_team_ground(match)
            is_home = team_ground["home"] == team
            opponent = team_ground["away"] if is_home else team_ground["home"]
            difficulty = float(self.__get_difficulty(opponent, is_home))

            difficulties.append(difficulty)

        average = round(sum(difficulties) / len(difficulties), 1)
        text = f"{average} {str(difficulties)}"

        return text

    def __get_teams(self):
        with open("data/team_difficulty.json") as json_file:
            data = json.load(json_file)

        return data[self.league]

    def __get_gw(self):
        df = self.fixtures_df
        df_where_no_stats = df[df["stats"] == "[]"]
        current_gw = df_where_no_stats["event"].iloc[0]

        return current_gw

    def __get_match(self, team, gw):
        df = self.fixtures_df[self.fixtures_df["event"] == gw]
        match = df[(df["team_a"] == team) | (df["team_h"] == team)]

        return match

    def __get_team_ground(self, match):        
        return {
            "home": match["team_h"].loc[match.index[0]],
            "away": match["team_a"].loc[match.index[0]],
        }

    def __get_difficulty(self, opponent, is_home):
        difficulty = self.teams[opponent]

        difficulty = difficulty * 1.5 if not is_home else difficulty

        return float(difficulty)
