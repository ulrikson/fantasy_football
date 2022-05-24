import requests
import pandas as pd


class Download:
    def __init__(self, league):
        self.league = league

        self.elements_df = None
        self.element_types_df = None
        self.teams_df = None

    def download(self):
        if self.league == "fpl":
            url = "https://fantasy.premierleague.com/api/bootstrap-static/"
        elif self.league == "fal":
            url = "https://fantasy.allsvenskan.se/api/bootstrap-static/"

        json = self.__get_json(url)
        self.__create_dfs(json)
        self.__save_dfs()

    def __get_json(self, url):
        response = requests.get(url)
        json = response.json()

        return json

    def __create_dfs(self, json):
        self.elements_df = pd.DataFrame(json["elements"])
        self.element_types_df = pd.DataFrame(json["element_types"])
        self.teams_df = pd.DataFrame(json["teams"])

        self.__map_values()

    def __map_values(self):
        df = self.elements_df

        df["element_type"] = df.element_type.map(
            self.element_types_df.set_index("id").singular_name
        )

        df["team"] = df.team.map(self.teams_df.set_index("id").name)

        self.elements_df = df

    def __save_dfs(self):
        self.elements_df.to_csv("data/players_" + self.league + ".csv", ",")


Download("fal").download()
