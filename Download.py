import requests
import pandas as pd


class Download:
    def __init__(self) -> None:
        pass

    def get_json(self, url):
        response = requests.get(url)
        json = response.json()

        return json

    def save_df(self, df, location):
        df.to_csv(location, ",")


class PlayerDownload(Download):
    def __init__(self, league):
        super().__init__()
        self.league = league

        self.players_df = None
        self.element_types_df = None
        self.teams_df = None

    def download(self):
        if self.league == "fpl":
            url = "https://fantasy.premierleague.com/api/bootstrap-static/"
        elif self.league == "fal":
            url = "https://fantasy.allsvenskan.se/api/bootstrap-static/"

        json = self.get_json(url)
        self.__create_dfs(json)

        self.save_df(self.players_df, "data/players_" + self.league + ".csv")
        self.save_df(self.teams_df, "data/teams_" + self.league + ".csv")

    def __create_dfs(self, json):
        self.players_df = pd.DataFrame(json["elements"])
        self.element_types_df = pd.DataFrame(json["element_types"])
        self.teams_df = pd.DataFrame(json["teams"])

        self.__map_values_players()
        self.__replace_translation()
        self.__string_to_float()
        self.__get_value_adjusted()

    def __map_values_players(self):
        df = self.players_df

        df["element_type"] = df.element_type.map(
            self.element_types_df.set_index("id").singular_name
        )

        df["team"] = df.team.map(self.teams_df.set_index("id").name)

        self.players_df = df

    def __replace_translation(self):
        df = self.players_df

        df["element_type"] = df["element_type"].replace(
            {
                "Målvakt": "Goalkeeper",
                "Försvarare": "Defender",
                "Mittfältare": "Midfielder",
                "Anfallare": "Forward",
            }
        )

        self.players_df = df

    def __string_to_float(self):
        df = self.players_df

        columnsShouldBeFloat = [
            "points_per_game",
            "now_cost",
            "minutes",
            "value_season",
            "total_points",
            "form",
        ]

        if self.league == "fpl":
            columnsShouldBeFloat.append("ict_index")
            columnsShouldBeFloat.append("ep_next")

        for column in columnsShouldBeFloat:
            df[column] = df[column].astype(float)

        self.players_df = df

    def __get_value_adjusted(self):
        df = self.players_df

        df["value_season_adj"] = round(
            (df["value_season"] / (df["total_points"] / df["points_per_game"]) * 10), 1
        )  # * 10 since it's just easier

        self.players_df = df


class FixtureDownload(Download):
    def __init__(self, league):
        super().__init__()
        self.league = league

        self.teams_df = pd.read_csv("data/teams_" + league + ".csv")
        self.fixtures_df = None

    def download(self):
        total_events = 38 if self.league == "fpl" else 30

        for i in range(1, total_events + 1):
            if self.league == "fpl":
                url = "https://fantasy.premierleague.com/api/fixtures/?event=" + str(i)
            elif self.league == "fal":
                url = "https://fantasy.allsvenskan.se/api/fixtures/?event=" + str(i)

            json = self.get_json(url)

            df_gw = pd.DataFrame(json)
            df_gw = self.__map_values(df_gw)

            if i == 1:
                self.fixtures_df = df_gw
            else:
                self.fixtures_df = pd.concat([self.fixtures_df, df_gw])

        self.save_df(self.fixtures_df, "data/fixtures_" + self.league + ".csv")

    def __map_values(self, df):
        df["team_h"] = df.team_h.map(self.teams_df.set_index("id").name)
        df["team_a"] = df.team_a.map(self.teams_df.set_index("id").name)

        return df
