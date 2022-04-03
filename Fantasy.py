import pandas as pd
import numpy as np
import requests

import matplotlib.pyplot as plt

plt.style.use("ggplot")

import seaborn as sns

sns.set_theme(color_codes=True)

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

        df = self.replaceTranslation(df)

        df = self.removeUnwantedTeams(df)
        df = self.stringToFloat(df)

        df = df[df["now_cost"] < self.max_cost]

        df = self.getValueAdjusted(df)

        df = self.removeLowValues(df)

        return df

    def replaceTranslation(self, df):
        df["element_type"] = df["element_type"].replace(
            {
                "Målvakt": "Goalkeeper",
                "Försvarare": "Defender",
                "Mittfältare": "Midfielder",
                "Anfallare": "Forward",
            }
        )

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

    def getValueAdjusted(self, df):
        df["value_season_adj"] = (
            df["value_season"] / (df["total_points"] / df["points_per_game"]) * 10
        )  # * 10 since it's just easier

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

    def getTopTeam(self):
        gk_df = self.dfFiltered("element_type", "Goalkeeper", "total_points").head(2)
        def_df = self.dfFiltered("element_type", "Defender", "total_points").head(5)
        mid_df = self.dfFiltered("element_type", "Midfielder", "total_points").head(5)
        fwd_df = self.dfFiltered("element_type", "Forward", "total_points").head(3)

        top = gk_df.append(def_df).append(mid_df).append(fwd_df)

        return top

    def getBarPlot(self, column, element):
        pivot = self.createPivot(column, element).sort_values(element)

        fig = plt.gcf()
        fig.set_size_inches(10, 8)

        sns.barplot(x=element, y=column, data=pivot)

    def getPlayerScatterPlot(self, position, x, y):
        df = self.dfFiltered("element_type", position, "value_season_adj")

        min = df["now_cost"].min()
        max = df["now_cost"].max()

        ax = sns.scatterplot(
            x=x, y=y, data=df, size="now_cost", sizes=(min, max), hue="team"
        )

        fig = plt.gcf()
        fig.set_size_inches(20, 10)
        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

        for i, txt in enumerate(df.web_name):
            ax.annotate(txt, (df[x].iat[i], df[y].iat[i]))

    def getMVPScatterPlot(self):
        x = "form"
        y = "value_season_adj"

        top_gk = self.dfFiltered("element_type", "Goalkeeper", "total_points").head()
        top_def = self.dfFiltered("element_type", "Defender", "total_points").head()
        top_mid = self.dfFiltered("element_type", "Midfielder", "total_points").head()
        top_fwd = self.dfFiltered("element_type", "Forward", "total_points").head()

        df = top_gk.append(top_def).append(top_mid).append(top_fwd)

        min = df["now_cost"].min()
        max = df["now_cost"].max()

        ax = sns.scatterplot(
            x=x, y=y, data=df, hue="element_type", size="now_cost", sizes=(min, max)
        )

        fig = plt.gcf()
        fig.set_size_inches(20, 10)

        for i, txt in enumerate(df.web_name):
            ax.annotate(txt, (df[x].iat[i], df[y].iat[i]))
