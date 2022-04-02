import pandas as pd
import numpy as np
import requests

import matplotlib.pyplot as plt
plt.style.use('ggplot')

import warnings
warnings.filterwarnings("ignore")


class Fantasy:
    def __init__(self, league, unwanted_teams, higher_than, max_cost):
        self.league = league

        self.json = self.getJson()
        self.elements_df = pd.DataFrame(self.json["elements"])
        self.elements_types_df = pd.DataFrame(self.json["element_types"])
        self.teams_df = pd.DataFrame(self.json["teams"])

        self.unwanted_teams = unwanted_teams
        self.higher_than = higher_than
        self.max_cost = max_cost

    def getJson(self):
        if self.league == "fpl":
            url = "https://fantasy.premierleague.com/api/bootstrap-static/"
        else:
            url = "https://fantasy.allsvenskan.se/api/bootstrap-static/"

        response = requests.get(url)
        json = response.json()

        return json

    def getPlayerDf(self):
        df = self.elements_df[
            [
                "web_name",
                "team",
                "element_type",
                "points_per_game",
                "now_cost",
                "minutes",
                "value_season",
                "total_points",
                "form",
                "value_form",
            ]
        ]

        df["element_type"] = df.element_type.map(
            self.elements_types_df.set_index("id").singular_name
        )

        df["team"] = df.team.map(self.teams_df.set_index("id").name)

        df["element_type"] = df["element_type"].replace(
            {
                "Målvakt": "Goalkeeper",
                "Försvarare": "Defender",
                "Mittfältare": "Midfielder",
                "Anfallare": "Forward",
            }
        )

        df = self.removeUnwantedTeams(df)
        df = self.stringToFloat(df)

        df["value_season_adj"] = df["value_season"] / (
            df["total_points"] / df["points_per_game"]
        )

        df = df[df["now_cost"] < self.max_cost]

        df = self.removeLowValues(df)

        return df

    def removeUnwantedTeams(self, df):
        for team in self.unwanted_teams:
            df = df.loc[df.team != team]

        return df

    def stringToFloat(self, df):
        columnsShouldBeFloat = [
            "points_per_game",
            "now_cost",
            "minutes",
            "value_season",
            "total_points",
            "form",
            "value_form",
        ]
        for column in columnsShouldBeFloat:
            df[column] = df[column].astype(float)

        return df

    def removeLowValues(self, df):
        for key, value in self.higher_than.items():
            df = df.loc[df[key] > value]

        return df

    def createPivot(self, index, value):
        df = self.getPlayerDf()

        pivot = df.pivot_table(index=index, values=value, aggfunc=np.mean).reset_index()

        pivot = pivot.sort_values(value, ascending=False)

        return pivot

    def dfFiltered(self, column, element, sort_by):
        df = self.getPlayerDf()
        df = df.loc[df[column] == element]
        df = df.sort_values(sort_by, ascending=False)

        return df
    
    def getBarPlot(self, column, element):
        pivot = self.createPivot(column, element).sort_values(element)

        pivot.plot(kind='barh', x=column, figsize=(10, 6))


    def getScatterPlot(self,position, x, y):
        df = self.dfFiltered('element_type', position, 'value_season_adj')

        ax = df.plot.scatter(x=x, y=y, alpha=.5, figsize=(
            20, 10), title=f"{position}: {x} v {y}")

        for i, txt in enumerate(df.web_name):
            ax.annotate(txt, (df[x].iat[i], df[y].iat[i]))

        plt.grid(which='both', axis='both', ls='-')
        plt.show()
